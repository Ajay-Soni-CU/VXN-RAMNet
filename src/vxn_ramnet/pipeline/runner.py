from __future__ import annotations
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import numpy as np

from vxn_ramnet.algorithms.decision import aggregate_windows, decide
from vxn_ramnet.algorithms.junction import ConstrainedJunctionDetector, candidate_to_dict, junction_confidence
from vxn_ramnet.algorithms.scoring import branch_windows, component_score, select_diverse_top_windows
from vxn_ramnet.algorithms.segmentation import build_segments
from vxn_ramnet.algorithms.similarity import flip_aware_similarity, suppress_diagonal
from vxn_ramnet.algorithms.turnaround import ReverseSequenceTurnaroundDetector, turnaround_confidence, turnaround_to_dict
from vxn_ramnet.config.models import PipelineConfig
from vxn_ramnet.core.enums import ComponentKind
from vxn_ramnet.core.exceptions import InsufficientEvidenceError, StageExecutionError
from vxn_ramnet.core.types import EncodedSequence
from vxn_ramnet.core.version import ARTIFACT_SCHEMA_VERSION
from vxn_ramnet.io.atomic import atomic_write_json
from vxn_ramnet.io.checksums import short_digest
from vxn_ramnet.io.paths import remove_managed_subdirectory
from vxn_ramnet.io.video import extract_evenly_spaced_frames, inspect_video
from vxn_ramnet.memory.store import RouteMemoryStore
from vxn_ramnet.observability import build_run_manifest, configure_logging
from vxn_ramnet.reporting import write_final_reports
from vxn_ramnet.vision import EfficientNetB0VisualEncoder, VisualEncoder, encode_sequence
from .artifacts import ArtifactStore
from .serialization import load_encoded_sequence, save_encoded_sequence

@dataclass(frozen=True)
class PipelineResult:
    run_id: str
    run_directory: Path
    report_files: dict[str, str]
    summary: dict[str, Any]


def _generated_run_id(config: PipelineConfig) -> str:
    timestamp=datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    identity="|".join([config.learning_video.id,*[q.id for q in config.query_videos],timestamp])
    return f"run-{timestamp}-{short_digest(identity,6)}"

class VxnPipeline:
    """Reproducible runner for the constrained camera-only VXN-RAMNet baseline.

    The encoder is injectable, allowing deterministic unit/integration tests without
    TensorFlow. The production default is a frozen EfficientNetB0 adapter.
    """
    def __init__(self, config: PipelineConfig, encoder: VisualEncoder | None = None):
        self.config=config
        self._encoder=encoder
        self.logger=None

    def _preflight(self)->tuple[dict,dict[str,Path]]:
        inputs={self.config.learning_video.id:self.config.resolve_input(self.config.learning_video)}
        inputs.update({item.id:self.config.resolve_input(item) for item in self.config.query_videos})
        resolved=list(inputs.values())
        if len({path.resolve() for path in resolved})!=len(resolved):
            raise ValueError("Each sequence must reference a distinct video file")
        reports={key:asdict(inspect_video(path,self.config.frames)) for key,path in inputs.items()}
        for report in reports.values(): report["path"]=Path(report["path"]).as_posix()
        return {"validated_at":datetime.now(timezone.utc).isoformat(),"videos":reports},inputs

    def _encoder_instance(self)->VisualEncoder:
        if self._encoder is None: self._encoder=EfficientNetB0VisualEncoder(self.config.encoder)
        return self._encoder

    def _extract(self, store:ArtifactStore, inputs:dict[str,Path])->dict:
        layout=store.layout
        report_path=layout.frame_report
        if self.config.artifacts.resume and store.is_complete("01-frame-extraction",[report_path]):
            return json.loads(report_path.read_text(encoding="utf-8"))
        with store.stage("01-frame-extraction"):
            learning_dir=layout.frames/"learning"/self.config.learning_video.id
            learning=extract_evenly_spaced_frames(inputs[self.config.learning_video.id],learning_dir,self.config.frames.learning_count,self.config.frames.learning_max_seconds,self.config.frames)
            queries={}
            for item in self.config.query_videos:
                queries[item.id]=extract_evenly_spaced_frames(inputs[item.id],layout.frames/"queries"/item.id,self.config.frames.query_count,self.config.frames.query_max_seconds,self.config.frames)
            report={"schema_version":ARTIFACT_SCHEMA_VERSION,"learning":{"id":self.config.learning_video.id,**learning},"queries":queries}
            atomic_write_json(report_path,report)
            return report

    def _embedding_paths(self, layout, sequence_id:str, learning:bool=False)->tuple[Path,Path]:
        base=layout.embeddings/("learning" if learning else "queries")
        return base/f"{sequence_id}.npz",base/f"{sequence_id}.json"

    def _encode(self, store:ArtifactStore, frame_report:dict)->tuple[EncodedSequence,dict[str,EncodedSequence],dict]:
        layout=store.layout
        all_outputs=[]
        learn_arrays,learn_meta=self._embedding_paths(layout,self.config.learning_video.id,True); all_outputs += [learn_arrays,learn_meta]
        for item in self.config.query_videos: all_outputs += list(self._embedding_paths(layout,item.id,False))
        if self.config.artifacts.resume and store.is_complete("02-visual-encoding",all_outputs):
            learning=load_encoded_sequence(self.config.learning_video.id,learn_arrays,learn_meta)
            queries={item.id:load_encoded_sequence(item.id,*self._embedding_paths(layout,item.id,False)) for item in self.config.query_videos}
            return learning,queries,learning.metadata.get("encoder",{})
        with store.stage("02-visual-encoding"):
            encoder=self._encoder_instance()
            learning_frames=[Path(path) for path in frame_report["learning"]["frame_paths"]]
            learning=encode_sequence(self.config.learning_video.id,learning_frames,encoder)
            save_encoded_sequence(learning,learn_arrays,learn_meta)
            queries={}
            for item in self.config.query_videos:
                frames=[Path(path) for path in frame_report["queries"][item.id]["frame_paths"]]
                sequence=encode_sequence(item.id,frames,encoder)
                save_encoded_sequence(sequence,*self._embedding_paths(layout,item.id,False)); queries[item.id]=sequence
            return learning,queries,encoder.manifest

    def _learn_memory(self, store:ArtifactStore, learning:EncodedSequence):
        layout=store.layout
        outputs=[layout.memory_arrays,layout.memory_metadata]
        if self.config.artifacts.resume and store.is_complete("03-route-memory",outputs):
            return RouteMemoryStore.load(*outputs)
        with store.stage("03-route-memory"):
            settings=self.config.detection
            similarity=flip_aware_similarity(learning.embeddings,learning.flipped_embeddings,learning.embeddings,learning.flipped_embeddings,settings.self_similarity_chunk_size)
            similarity=suppress_diagonal(similarity,max(8,int(0.035*len(learning.embeddings))))
            junction,top_junctions=ConstrainedJunctionDetector(settings).detect(similarity)
            turnaround,top_turnarounds=ReverseSequenceTurnaroundDetector(settings).detect(learning.embeddings,learning.flipped_embeddings,junction.first_index,junction.return_index)
            segments=build_segments(len(learning.embeddings),junction.first_index,turnaround.index,junction.return_index,settings)
            quality={"junction_score":junction.raw_score,"junction_confidence":junction_confidence(junction.raw_score,settings),"backtrack_score":turnaround.raw_score,"backtrack_confidence":turnaround_confidence(turnaround.raw_score,settings)}
            if self.config.runtime.fail_on_degraded_graph and (quality["junction_confidence"]=="low" or quality["backtrack_confidence"]=="low"):
                raise InsufficientEvidenceError(f"Graph quality gate failed: {quality}")
            segment_map={ComponentKind.COMMON_PATH:segments.common,ComponentKind.JUNCTION:segments.junction,ComponentKind.BRANCH_A:segments.branch_a,ComponentKind.BACKTRACK:segments.backtrack,ComponentKind.BRANCH_B:segments.branch_b}
            display={ComponentKind.COMMON_PATH:"COMMON_PATH",ComponentKind.JUNCTION:"JUNCTION_A",ComponentKind.BRANCH_A:self.config.branch_a_name,ComponentKind.BACKTRACK:"BACKTRACK_TO_JUNCTION",ComponentKind.BRANCH_B:self.config.branch_b_name}
            metadata={"mode":"constrained_single_junction_backtracking","topology_limit":"one junction and two exploration-order branches","segment_policy":settings.segment_policy,
                "events":{"first_junction_index":junction.first_index,"turnaround_index":turnaround.index,"return_junction_index":junction.return_index},"quality":quality,
                "segments":segments.as_ranges(),"component_counts":{kind.value:len(values) for kind,values in segment_map.items()},"top_junction_candidates":[candidate_to_dict(c) for c in top_junctions],"top_turnaround_candidates":[turnaround_to_dict(c) for c in top_turnarounds],
                "branch_label_note":"Branch names describe exploration order, not validated physical left/right direction.","encoder":learning.metadata.get("encoder",{})}
            memory=RouteMemoryStore.build(learning.embeddings,learning.flipped_embeddings,segment_map,display,metadata)
            RouteMemoryStore.save(memory,layout.memory_arrays,layout.memory_metadata)
            if self.config.artifacts.save_self_similarity_matrix:
                from vxn_ramnet.io.npz import save_npz
                save_npz(layout.root/"memory"/"self-similarity.npz",{"self_similarity":similarity.astype(np.float32)})
            return memory

    def _classify_query(self, query:EncodedSequence, memory)->dict:
        components=memory.components; rows=[]
        for start,end in branch_windows(len(query.embeddings)):
            q=query.embeddings[start:end]; qf=query.flipped_embeddings[start:end]
            scores={}
            for key,kind in (("branch_a",ComponentKind.BRANCH_A),("branch_b",ComponentKind.BRANCH_B),("common",ComponentKind.COMMON_PATH),("junction",ComponentKind.JUNCTION)):
                component=components[kind]
                scores[key],_=component_score(q,qf,component.embeddings,component.flipped_embeddings,component.centroid,self.config.detection.self_similarity_chunk_size)
            best=max(scores["branch_a"],scores["branch_b"]); gap=abs(scores["branch_a"]-scores["branch_b"]); shared=max(scores["common"],scores["junction"])
            rows.append({"start":start,"end":end,"frame_count":end-start,"branch_a_score":scores["branch_a"],"branch_b_score":scores["branch_b"],"common_score":scores["common"],"junction_score":scores["junction"],"best_branch_score":best,"branch_gap":gap,"shared_score":shared,"window_quality":best+0.70*gap-0.25*shared+0.03*(start/max(1,len(query.embeddings)))})
        if not rows: raise InsufficientEvidenceError(f"No classification windows for query {query.sequence_id}")
        if self.config.decision.window_selection=="legacy_best": selected=[max(rows,key=lambda row:row["window_quality"])]
        else: selected=select_diverse_top_windows(rows,self.config.decision.top_k_windows)
        aggregate=aggregate_windows(rows,selected)
        evidence={"selected_windows":[{"start":r["start"],"end":r["end"],"quality":r["window_quality"]} for r in selected],"all_windows":sorted(rows,key=lambda row:row["window_quality"],reverse=True),"aggregation":self.config.decision.window_selection}
        decision=decide(aggregate,self.config.decision,self.config.branch_a_name,self.config.branch_b_name,evidence)
        return {"query_id":query.sequence_id,"decision_kind":decision.kind.value,"branch_id":decision.branch_id,"confidence":decision.confidence,"reason":decision.reason,
            "branch_a_score":aggregate.branch_a,"branch_b_score":aggregate.branch_b,"branch_gap":aggregate.gap,"common_score":aggregate.common,"junction_score":aggregate.junction,"selected_windows":len(selected),"evidence":decision.evidence}

    def _classify(self, store:ArtifactStore, queries:dict[str,EncodedSequence], memory)->list[dict]:
        output=store.layout.reports/"query-decisions.json"
        query_paths=[store.layout.reports/"queries"/f"{query_id}.json" for query_id in queries]
        if self.config.artifacts.resume and store.is_complete("04-query-classification",[output,*query_paths]):
            return json.loads(output.read_text(encoding="utf-8"))["queries"]
        with store.stage("04-query-classification"):
            reports=[]
            for query_id,sequence in queries.items():
                report=self._classify_query(sequence,memory); reports.append(report); atomic_write_json(store.layout.reports/"queries"/f"{query_id}.json",report)
            atomic_write_json(output,{"schema_version":ARTIFACT_SCHEMA_VERSION,"queries":reports})
            return reports

    def run(self)->PipelineResult:
        preflight,inputs=self._preflight()  # all inputs are validated before any managed output is removed/created
        run_id=self.config.artifacts.run_id or _generated_run_id(self.config)
        if self.config.artifacts.resume and self.config.artifacts.run_id is None: raise ValueError("resume requires an explicit artifacts.run_id")
        store=ArtifactStore.create(
            self.config.resolved_output_root,
            run_id,
            self.config.artifacts.overwrite_existing_run,
            self.config.artifacts.resume,
            self.config.runtime.include_diagnostic_details,
        )
        self.logger=configure_logging(self.config.runtime.log_level,store.layout.logs)
        atomic_write_json(store.layout.config,self.config.model_dump(mode="json")); atomic_write_json(store.layout.preflight,preflight)
        self.logger.info("Starting VXN-RAMNet run %s",run_id)
        try:
            frame_report=self._extract(store,inputs)
            learning,queries,model_manifest=self._encode(store,frame_report)
            atomic_write_json(store.layout.manifest,build_run_manifest(run_id,inputs,model_manifest))
            memory=self._learn_memory(store,learning)
            query_reports=self._classify(store,queries,memory)
            summary={"schema_version":ARTIFACT_SCHEMA_VERSION,"run_id":run_id,"system":"VXN-RAMNet","implementation_status":"camera-only constrained research baseline","route_memory":memory.metadata,"query_results":query_reports}
            with store.stage("05-reporting"):
                report_files=write_final_reports(store.layout.reports,summary)
            if not self.config.artifacts.save_frames:
                remove_managed_subdirectory(store.layout.frames, store.layout.root)
            final=json.loads(Path(report_files["json"]).read_text(encoding="utf-8"))
            self.logger.info("Run complete: %s",report_files["markdown"])
            return PipelineResult(run_id,store.layout.root,report_files,final)
        except Exception as exc:
            if self.config.runtime.include_diagnostic_details:
                self.logger.exception("Pipeline failed")
            else:
                self.logger.error("Pipeline failed (%s). Diagnostic details are redacted.", type(exc).__name__)
            raise StageExecutionError(
                f"Pipeline failed in run {run_id} ({type(exc).__name__}). Review the stage state and local log."
            ) from exc


def run_pipeline(config:PipelineConfig, encoder:VisualEncoder|None=None)->PipelineResult:
    return VxnPipeline(config,encoder).run()
