from dataclasses import dataclass
from enum import Enum
from typing import Mapping, Set


class DisputeTransitionError(ValueError):
    pass


class DisputeStatus(str, Enum):
    OPEN = "open"
    EVIDENCE_COLLECTION = "evidence_collection"
    UNDER_REVIEW = "under_review"
    DECISION = "decision"
    RESOLVED = "resolved"


class DisputeActor(str, Enum):
    PARTICIPANT = "participant"
    ADMIN = "admin"
    SYSTEM = "system"


class DisputeAction(str, Enum):
    ADD_EVIDENCE = "add_evidence"
    SUBMIT_FOR_REVIEW = "submit_for_review"
    RECORD_DECISION = "record_decision"
    CONFIRM_RESOLUTION = "confirm_resolution"


class DisputeDecision(str, Enum):
    NO_FINANCIAL_ADJUSTMENT = "no_financial_adjustment"
    RELEASE_DEPOSIT = "release_deposit"
    PARTIAL_DEPOSIT_CAPTURE = "partial_deposit_capture"
    FULL_DEPOSIT_CAPTURE = "full_deposit_capture"


@dataclass(frozen=True)
class DisputeRule:
    target: DisputeStatus
    actors: Set[DisputeActor]


TRANSITIONS: Mapping[DisputeStatus, Mapping[DisputeAction, DisputeRule]] = {
    DisputeStatus.OPEN: {
        DisputeAction.ADD_EVIDENCE: DisputeRule(
            DisputeStatus.EVIDENCE_COLLECTION,
            {DisputeActor.PARTICIPANT, DisputeActor.ADMIN, DisputeActor.SYSTEM},
        ),
    },
    DisputeStatus.EVIDENCE_COLLECTION: {
        DisputeAction.SUBMIT_FOR_REVIEW: DisputeRule(
            DisputeStatus.UNDER_REVIEW,
            {DisputeActor.PARTICIPANT, DisputeActor.ADMIN},
        ),
    },
    DisputeStatus.UNDER_REVIEW: {
        DisputeAction.RECORD_DECISION: DisputeRule(
            DisputeStatus.DECISION, {DisputeActor.ADMIN},
        ),
    },
    DisputeStatus.DECISION: {
        DisputeAction.CONFIRM_RESOLUTION: DisputeRule(
            DisputeStatus.RESOLVED, {DisputeActor.ADMIN, DisputeActor.SYSTEM},
        ),
    },
    DisputeStatus.RESOLVED: {},
}


def transition(current: str, action: DisputeAction, actor: DisputeActor) -> DisputeStatus:
    try:
        status = DisputeStatus(current)
    except ValueError as exc:
        raise DisputeTransitionError(f"Unknown dispute status: {current}") from exc
    rule = TRANSITIONS[status].get(action)
    if not rule:
        raise DisputeTransitionError(f"Action {action.value} is not allowed from {status.value}")
    if actor not in rule.actors:
        raise DisputeTransitionError(f"Actor {actor.value} cannot perform {action.value}")
    return rule.target


def expected_deposit_status(decision: str) -> str | None:
    return {
        DisputeDecision.RELEASE_DEPOSIT.value: "released",
        DisputeDecision.PARTIAL_DEPOSIT_CAPTURE.value: "partially_captured",
        DisputeDecision.FULL_DEPOSIT_CAPTURE.value: "captured",
    }.get(decision)
