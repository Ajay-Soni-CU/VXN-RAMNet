from vxn_ramnet.algorithms.decision import AggregatedScores, decide
from vxn_ramnet.config.models import DecisionSettings
from vxn_ramnet.core.enums import DecisionKind


def test_known_branch_decision():
    result = decide(AggregatedScores(0.80, 0.60, 0.20, 0.80, 0.30, 0.35), DecisionSettings(), "A", "B", {})
    assert result.kind is DecisionKind.KNOWN_BRANCH
    assert result.branch_id == "A"
    assert result.confidence is not None


def test_uncertain_decision():
    result = decide(AggregatedScores(0.70, 0.69, 0.01, 0.70, 0.30, 0.35), DecisionSettings(), "A", "B", {})
    assert result.kind is DecisionKind.UNCERTAIN


def test_unknown_decision():
    result = decide(AggregatedScores(0.30, 0.20, 0.10, 0.30, 0.30, 0.35), DecisionSettings(), "A", "B", {})
    assert result.kind is DecisionKind.UNKNOWN_ROUTE
