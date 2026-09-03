from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Dict, FrozenSet

from fastapi import HTTPException, status


class BookingStatus(str, Enum):
    DRAFT = "brouillon"
    PENDING_OWNER = "en_attente_approbation"
    ACCEPTED = "acceptee"
    PAYMENT_PENDING = "paiement_en_attente"
    CONFIRMED = "confirmee"
    READY_FOR_HANDOVER = "prete_remise"
    ACTIVE = "en_cours"
    RETURN_PENDING = "en_attente_validation"
    COMPLETED = "termine"
    REJECTED = "rejete"
    CANCELLED = "annule"
    DISPUTED = "en_litige"
    RESOLVED = "resolu"


class BookingAction(str, Enum):
    SUBMIT = "submit"
    OWNER_ACCEPT = "owner_accept"
    OWNER_REJECT = "owner_reject"
    START_PAYMENT = "start_payment"
    CONFIRM_PAYMENT = "confirm_payment"
    MARK_READY = "mark_ready"
    COMPLETE_HANDOVER = "complete_handover"
    REQUEST_RETURN = "request_return"
    COMPLETE_RETURN = "complete_return"
    CANCEL = "cancel"
    OPEN_DISPUTE = "open_dispute"
    RESOLVE_DISPUTE = "resolve_dispute"


class BookingActor(str, Enum):
    RENTER = "renter"
    OWNER = "owner"
    ADMIN = "admin"
    SYSTEM = "system"


@dataclass(frozen=True)
class TransitionRule:
    target: BookingStatus
    actors: FrozenSet[BookingActor]


PARTICIPANTS = frozenset({BookingActor.RENTER, BookingActor.OWNER, BookingActor.ADMIN})
SERVER_ONLY = frozenset({BookingActor.SYSTEM, BookingActor.ADMIN})


class BookingStateMachine:
    BLOCKING_STATUSES = frozenset({
        BookingStatus.ACCEPTED.value,
        BookingStatus.PAYMENT_PENDING.value,
        BookingStatus.CONFIRMED.value,
        BookingStatus.READY_FOR_HANDOVER.value,
        BookingStatus.ACTIVE.value,
        BookingStatus.RETURN_PENDING.value,
        BookingStatus.DISPUTED.value,
    })

    TRANSITIONS: Dict[BookingStatus, Dict[BookingAction, TransitionRule]] = {
        BookingStatus.DRAFT: {
            BookingAction.SUBMIT: TransitionRule(BookingStatus.PENDING_OWNER, frozenset({BookingActor.RENTER, BookingActor.SYSTEM, BookingActor.ADMIN})),
            BookingAction.CANCEL: TransitionRule(BookingStatus.CANCELLED, PARTICIPANTS),
        },
        BookingStatus.PENDING_OWNER: {
            BookingAction.OWNER_ACCEPT: TransitionRule(BookingStatus.ACCEPTED, frozenset({BookingActor.OWNER, BookingActor.ADMIN})),
            BookingAction.OWNER_REJECT: TransitionRule(BookingStatus.REJECTED, frozenset({BookingActor.OWNER, BookingActor.ADMIN})),
            BookingAction.CANCEL: TransitionRule(BookingStatus.CANCELLED, PARTICIPANTS),
        },
        BookingStatus.ACCEPTED: {
            BookingAction.START_PAYMENT: TransitionRule(BookingStatus.PAYMENT_PENDING, SERVER_ONLY),
            BookingAction.CANCEL: TransitionRule(BookingStatus.CANCELLED, PARTICIPANTS),
        },
        BookingStatus.PAYMENT_PENDING: {
            BookingAction.CONFIRM_PAYMENT: TransitionRule(BookingStatus.CONFIRMED, SERVER_ONLY),
            BookingAction.CANCEL: TransitionRule(BookingStatus.CANCELLED, PARTICIPANTS),
        },
        BookingStatus.CONFIRMED: {
            BookingAction.MARK_READY: TransitionRule(BookingStatus.READY_FOR_HANDOVER, frozenset({BookingActor.OWNER, BookingActor.SYSTEM, BookingActor.ADMIN})),
            BookingAction.CANCEL: TransitionRule(BookingStatus.CANCELLED, PARTICIPANTS),
            BookingAction.OPEN_DISPUTE: TransitionRule(BookingStatus.DISPUTED, PARTICIPANTS),
        },
        BookingStatus.READY_FOR_HANDOVER: {
            BookingAction.COMPLETE_HANDOVER: TransitionRule(BookingStatus.ACTIVE, SERVER_ONLY),
            BookingAction.CANCEL: TransitionRule(BookingStatus.CANCELLED, PARTICIPANTS),
            BookingAction.OPEN_DISPUTE: TransitionRule(BookingStatus.DISPUTED, PARTICIPANTS),
        },
        BookingStatus.ACTIVE: {
            BookingAction.REQUEST_RETURN: TransitionRule(BookingStatus.RETURN_PENDING, SERVER_ONLY),
            BookingAction.OPEN_DISPUTE: TransitionRule(BookingStatus.DISPUTED, PARTICIPANTS),
        },
        BookingStatus.RETURN_PENDING: {
            BookingAction.COMPLETE_RETURN: TransitionRule(BookingStatus.COMPLETED, SERVER_ONLY),
            BookingAction.OPEN_DISPUTE: TransitionRule(BookingStatus.DISPUTED, PARTICIPANTS),
        },
        BookingStatus.DISPUTED: {
            BookingAction.RESOLVE_DISPUTE: TransitionRule(BookingStatus.RESOLVED, SERVER_ONLY),
        },
        BookingStatus.COMPLETED: {
            BookingAction.OPEN_DISPUTE: TransitionRule(BookingStatus.DISPUTED, PARTICIPANTS),
        },
        BookingStatus.REJECTED: {},
        BookingStatus.CANCELLED: {},
        BookingStatus.RESOLVED: {},
    }

    LEGACY_STATUS_ALIASES = {
        "en_attente_verification": BookingStatus.DRAFT,
        "confirme_cod": BookingStatus.CONFIRMED,
        "litige": BookingStatus.DISPUTED,
        "draft": BookingStatus.DRAFT,
        "pending_owner": BookingStatus.PENDING_OWNER,
        "accepted": BookingStatus.ACCEPTED,
        "payment_pending": BookingStatus.PAYMENT_PENDING,
        "confirmed": BookingStatus.CONFIRMED,
        "ready_for_handover": BookingStatus.READY_FOR_HANDOVER,
        "active": BookingStatus.ACTIVE,
        "return_pending": BookingStatus.RETURN_PENDING,
        "completed": BookingStatus.COMPLETED,
        "rejected": BookingStatus.REJECTED,
        "cancelled": BookingStatus.CANCELLED,
        "disputed": BookingStatus.DISPUTED,
        "resolved": BookingStatus.RESOLVED,
    }

    LEGACY_TARGET_ACTIONS = {
        BookingStatus.ACCEPTED.value: BookingAction.OWNER_ACCEPT,
        "confirme_cod": BookingAction.OWNER_ACCEPT,
        BookingStatus.REJECTED.value: BookingAction.OWNER_REJECT,
        BookingStatus.CANCELLED.value: BookingAction.CANCEL,
        BookingStatus.DISPUTED.value: BookingAction.OPEN_DISPUTE,
        "litige": BookingAction.OPEN_DISPUTE,
        BookingStatus.PAYMENT_PENDING.value: BookingAction.START_PAYMENT,
        BookingStatus.CONFIRMED.value: BookingAction.CONFIRM_PAYMENT,
        BookingStatus.READY_FOR_HANDOVER.value: BookingAction.MARK_READY,
        BookingStatus.ACTIVE.value: BookingAction.COMPLETE_HANDOVER,
        BookingStatus.RETURN_PENDING.value: BookingAction.REQUEST_RETURN,
        BookingStatus.COMPLETED.value: BookingAction.COMPLETE_RETURN,
        BookingStatus.RESOLVED.value: BookingAction.RESOLVE_DISPUTE,
        "accepted": BookingAction.OWNER_ACCEPT,
        "payment_pending": BookingAction.START_PAYMENT,
        "confirmed": BookingAction.CONFIRM_PAYMENT,
        "ready_for_handover": BookingAction.MARK_READY,
        "active": BookingAction.COMPLETE_HANDOVER,
        "return_pending": BookingAction.REQUEST_RETURN,
        "completed": BookingAction.COMPLETE_RETURN,
        "rejected": BookingAction.OWNER_REJECT,
        "cancelled": BookingAction.CANCEL,
        "disputed": BookingAction.OPEN_DISPUTE,
        "resolved": BookingAction.RESOLVE_DISPUTE,
    }

    @classmethod
    def normalize_status(cls, value: str | BookingStatus) -> BookingStatus:
        if isinstance(value, BookingStatus):
            return value
        normalized_value = value.lower()
        if normalized_value in cls.LEGACY_STATUS_ALIASES:
            return cls.LEGACY_STATUS_ALIASES[normalized_value]
        try:
            return BookingStatus(normalized_value)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_CURRENT_STATUS", "message": f"Statut '{value}' inconnu."},
            ) from exc

    @classmethod
    def normalize_action(cls, value: str | BookingAction) -> BookingAction:
        if isinstance(value, BookingAction):
            return value
        try:
            return BookingAction(value)
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_BOOKING_ACTION", "message": f"Action '{value}' inconnue."},
            ) from exc

    @classmethod
    def action_for_legacy_target(cls, target_status: str) -> BookingAction:
        action = cls.LEGACY_TARGET_ACTIONS.get(target_status.lower())
        if not action:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_TARGET_STATUS", "message": f"Statut cible '{target_status}' inconnu."},
            )
        return action

    @classmethod
    def actor_for_user(cls, user, booking) -> BookingActor:
        if getattr(user, "user_role", None) == "admin":
            return BookingActor.ADMIN
        if user.id == booking.loueur_id:
            return BookingActor.OWNER
        if user.id == booking.locataire_id:
            return BookingActor.RENTER
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Accès réservation interdit.")

    @classmethod
    def validate_action(
        cls,
        current_status: str | BookingStatus,
        action: str | BookingAction,
        actor: BookingActor,
    ) -> BookingStatus:
        current = cls.normalize_status(current_status)
        normalized_action = cls.normalize_action(action)
        rule = cls.TRANSITIONS[current].get(normalized_action)
        if not rule:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "INVALID_STATE_TRANSITION",
                    "message": f"Action '{normalized_action.value}' interdite depuis '{current.value}'.",
                },
            )
        if actor not in rule.actors:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "TRANSITION_FORBIDDEN",
                    "message": f"L'acteur '{actor.value}' ne peut pas exécuter '{normalized_action.value}'.",
                },
            )
        return rule.target

    @classmethod
    def transition(cls, booking, action: str | BookingAction, actor: BookingActor) -> BookingStatus:
        target = cls.validate_action(booking.statut, action, actor)
        booking.statut = target.value
        booking.modifie_le = datetime.utcnow()
        return target

    @classmethod
    def validate_transition(cls, current_status: str, target_status: str) -> bool:
        """Compatibility validator; all mutations must use action-based transition()."""
        current = cls.normalize_status(current_status)
        target = cls.normalize_status(target_status)
        if not any(rule.target == target for rule in cls.TRANSITIONS[current].values()):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "code": "INVALID_STATE_TRANSITION",
                    "message": f"Transition interdite de '{current.value}' vers '{target.value}'.",
                },
            )
        return True


booking_state_machine = BookingStateMachine()
