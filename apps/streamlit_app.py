"""Optional local Streamlit interface for the camera baseline.

Run with: streamlit run apps/streamlit_app.py
This UI creates a unique temporary directory per browser session and never uses a
shared repository output folder. It is not an authenticated hosted service.
"""
from __future__ import annotations

import shutil
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from vxn_ramnet.config.models import PipelineConfig
from vxn_ramnet.pipeline import VxnPipeline

MAX_UPLOAD_BYTES = 750_000_000
ALLOWED_TYPES = ["mp4", "mov", "avi", "mkv", "webm"]


def session_root() -> Path:
    if "vxn_session_root" not in st.session_state:
        created = Path(tempfile.mkdtemp(prefix="vxn-session-"))
        (created / ".vxn-ui-session").write_text("managed session\n", encoding="utf-8")
        st.session_state.vxn_session_root = str(created)
    return Path(st.session_state.vxn_session_root)


def save_upload(upload, path: Path) -> None:
    data = upload.getvalue()
    if not data or len(data) > MAX_UPLOAD_BYTES:
        raise ValueError("Upload is empty or exceeds the configured size limit")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


st.set_page_config(page_title="VXN-RAMNet Research Runner", page_icon="🧭", layout="wide")
st.title("VXN-RAMNet camera baseline")
st.warning("Research prototype only. Branch A/B are exploration-order labels, not physical left/right guidance.")

learning = st.file_uploader("Learning journey", type=ALLOWED_TYPES)
queries = st.file_uploader("Query journeys", type=ALLOWED_TYPES, accept_multiple_files=True)
col1, col2 = st.columns(2)
with col1:
    learning_frames = st.number_input("Learning frames", min_value=40, max_value=1000, value=270, step=10)
with col2:
    query_frames = st.number_input("Frames per query", min_value=20, max_value=600, value=120, step=10)

if st.button("Run isolated session", type="primary"):
    if learning is None or not queries:
        st.error("Provide one learning journey and at least one query journey.")
        st.stop()
    root = session_root()
    input_dir = root / "inputs"
    try:
        learning_path = input_dir / f"learning{Path(learning.name).suffix.lower()}"
        save_upload(learning, learning_path)
        query_items = []
        for index, upload in enumerate(queries, start=1):
            query_id = f"query-{index:02d}"
            path = input_dir / f"{query_id}{Path(upload.name).suffix.lower()}"
            save_upload(upload, path)
            query_items.append({"id": query_id, "path": path})
        run_id = "run-" + datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
        config = PipelineConfig.model_validate({
            "project_root": root,
            "learning_video": {"id": "learning-route", "path": learning_path},
            "query_videos": query_items,
            "frames": {"learning_count": int(learning_frames), "query_count": int(query_frames)},
            "artifacts": {"output_root": root / "artifacts", "run_id": run_id, "save_frames": False},
        })
        with st.status("Running pipeline", expanded=True) as status:
            result = VxnPipeline(config).run()
            status.update(label="Run complete", state="complete")
        rows = [{key: row.get(key) for key in ("query_id", "decision_kind", "branch_id", "confidence", "reason")} for row in result.summary["query_results"]]
        st.dataframe(rows, use_container_width=True)
        for label, path in result.report_files.items():
            report = Path(path)
            st.download_button(f"Download {label}", report.read_bytes(), file_name=report.name)
    except Exception as exc:  # public UI intentionally avoids local paths and stack traces
        st.error(f"Pipeline failed ({type(exc).__name__}). Review the local structured log for diagnostic details.")

if st.button("Delete this session's temporary data"):
    root = session_root().resolve()
    temp_root = Path(tempfile.gettempdir()).resolve()
    marker = root / ".vxn-ui-session"
    try:
        root.relative_to(temp_root)
        safe = marker.is_file() and root.name.startswith("vxn-session-") and root != temp_root
    except ValueError:
        safe = False
    if safe:
        shutil.rmtree(root)
        st.session_state.pop("vxn_session_root", None)
        st.success("Temporary session data deleted.")
    else:
        st.error("Session cleanup was blocked because the directory was not recognized as managed.")
