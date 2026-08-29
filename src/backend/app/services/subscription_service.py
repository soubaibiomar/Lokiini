from typing import Dict, Any, List

class SubscriptionService:
    PLANS: Dict[str, Dict[str, Any]] = {
        "Gratuit": {
            "nom": "Gratuit",
            "prix_mensuel_mad": 0.0,
            "max_annonces": 3,
            "commission_pct": 0.15,
            "badge": None,
            "facturation_ice": False,
            "description": "Idéal pour les particuliers louant occasionnellement."
        },
        "Premium": {
            "nom": "Premium",
            "prix_mensuel_mad": 79.0,
            "max_annonces": 15,
            "commission_pct": 0.12,
            "badge": "Loueur Recommandé",
            "facturation_ice": True,
            "description": "Pour les loueurs réguliers souhaitant booster leur visibilité."
        },
        "Pro": {
            "nom": "Pro",
            "prix_mensuel_mad": 149.0,
            "max_annonces": 9999,
            "commission_pct": 0.07,
            "badge": "Loueur Pro Certifié",
            "facturation_ice": True,
            "description": "Pour entreprises & parcs de location avec annonces illimitées."
        },
        "Entreprise": {
            "nom": "Entreprise",
            "prix_mensuel_mad": 300.0,
            "max_annonces": 99999,
            "commission_pct": 0.05,
            "badge": "Grands Parcs & Flottes",
            "facturation_ice": True,
            "description": "Grands parcs de matériel et régies multi-villes."
        }
    }

    @classmethod
    def get_all_plans(cls) -> List[Dict[str, Any]]:
        return list(cls.PLANS.values())

    @classmethod
    def get_plan_details(cls, plan_name: str) -> Dict[str, Any]:
        return cls.PLANS.get(plan_name, cls.PLANS["Gratuit"])

subscription_service = SubscriptionService()
