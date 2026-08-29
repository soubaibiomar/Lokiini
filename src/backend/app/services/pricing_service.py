from datetime import date
from typing import Dict, Any, Optional

class PricingService:
    @staticmethod
    def calculate_duration_days(start_date: date, end_date: date) -> int:
        if end_date < start_date:
            raise ValueError("La date de fin ne peut pas être antérieure à la date de début.")
        return (end_date - start_date).days + 1

    @classmethod
    def compute_pricing_breakdown(
        cls,
        prix_par_jour: float,
        prix_par_semaine: Optional[float],
        prix_par_mois: Optional[float],
        montant_caution: float,
        start_date: date,
        end_date: date,
        is_pro_owner: bool = False
    ) -> Dict[str, Any]:
        """
        Calcule la ventilation financière détaillée avec remises dégressives :
        - 3+ jours  : -10% de remise sur le prix journalier
        - 7+ jours  : -15% (ou base tarif semaine)
        - 30+ jours : -25% (ou base tarif mois)
        Commission plateforme : 7% pour pro_owner, 15% pour owner particulier.
        """
        nb_jours = cls.calculate_duration_days(start_date, end_date)
        prix_base = float(prix_par_jour) * nb_jours
        remise_pct = 0.0
        applied_rate_type = "journalier"

        # 1. Calcul de la remise dégressive
        if nb_jours >= 30:
            remise_pct = 0.25
            applied_rate_type = "mensuel (-25%)"
            montant_brut = prix_base * (1.0 - remise_pct)
        elif nb_jours >= 7:
            remise_pct = 0.15
            applied_rate_type = "hebdomadaire (-15%)"
            montant_brut = prix_base * (1.0 - remise_pct)
        elif nb_jours >= 3:
            remise_pct = 0.10
            applied_rate_type = "court-sejour (-10%)"
            montant_brut = prix_base * (1.0 - remise_pct)
        else:
            montant_brut = prix_base

        # 2. Commission plateforme (7% pro / 15% particulier)
        commission_pct = 0.07 if is_pro_owner else 0.15
        frais_service_plateforme = round(montant_brut * commission_pct, 2)
        gains_net_loueur = round(montant_brut - frais_service_plateforme, 2)

        return {
            "nombre_jours": nb_jours,
            "prix_par_jour_base": round(float(prix_par_jour), 2),
            "total_brut_sans_remise": round(prix_base, 2),
            "remise_pourcentage": int(remise_pct * 100),
            "type_tarif_applique": applied_rate_type,
            "total_location_mad": round(montant_brut, 2),
            "frais_service_plateforme_mad": frais_service_plateforme,
            "commission_pourcentage": int(commission_pct * 100),
            "gains_net_loueur_mad": gains_net_loueur,
            "montant_caution_mad": round(float(montant_caution or 0.0), 2),
            "total_a_payer_a_la_remise_mad": round(montant_brut + float(montant_caution or 0.0), 2)
        }

pricing_service = PricingService()
