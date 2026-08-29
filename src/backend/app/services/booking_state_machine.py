from typing import Set, Dict
from fastapi import HTTPException, status

class BookingStateMachine:
    VALID_STATUSES = {
        "en_attente_approbation",
        "confirme_cod",
        "en_cours",
        "termine",
        "annule",
        "litige"
    }

    ALLOWED_TRANSITIONS: Dict[str, Set[str]] = {
        "en_attente_approbation": {"confirme_cod", "annule"},
        "confirme_cod": {"en_cours", "annule", "litige"},
        "en_cours": {"termine", "litige"},
        "litige": {"termine", "annule"}, # Résolu par médiation admin
        "termine": set(), # État final
        "annule": set()   # État final
    }

    @classmethod
    def validate_transition(cls, current_status: str, target_status: str) -> bool:
        if current_status not in cls.VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_CURRENT_STATUS", "message": f"Statut actuel '{current_status}' inconnu."}
            )
        if target_status not in cls.VALID_STATUSES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"code": "INVALID_TARGET_STATUS", "message": f"Statut cible '{target_status}' inconnu."}
            )
            
        allowed = cls.ALLOWED_TRANSITIONS.get(current_status, set())
        if target_status not in allowed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "code": "INVALID_STATE_TRANSITION",
                    "message": f"Transition interdite : impossible de passer de '{current_status}' à '{target_status}'."
                }
            )
        return True

booking_state_machine = BookingStateMachine()
