from datetime import datetime, timedelta
from typing import Dict, Any, List

class EarningsService:
    @classmethod
    def calculate_dashboard_metrics(
        cls,
        reservations_data: List[Dict[str, Any]],
        periode: str = "mois", # jour, semaine, mois, annee
        released_deposits_mad: float = 0,
    ) -> Dict[str, Any]:
        """Agrège les gains bruts, nets, commissions et taux d'occupation."""
        total_brut = 0.0
        total_commission = 0.0
        completed_count = 0
        pending_payout = 0.0
        article_earnings: Dict[str, float] = {}

        for r in reservations_data:
            statut = r.get("statut_reservation", "")
            payout_status = r.get("payout_status", "not_ready")
            if payout_status == "paid":
                prix = float(r.get("rental_amount", 0.0))
                frais = float(r.get("platform_fee", 0.0))
                total_brut += prix
                total_commission += frais
                art_title = r.get("article_titre", "Matériel")
                article_earnings[art_title] = article_earnings.get(art_title, 0.0) + prix
            elif payout_status == "pending":
                pending_payout += float(r.get("payout_amount", 0.0))
            if statut == "termine":
                completed_count += 1

        gains_nets = total_brut - total_commission
        
        # Sort top articles
        top_articles = [
            {"titre": k, "revenus_generes_mad": round(v, 2)}
            for k, v in sorted(article_earnings.items(), key=lambda item: item[1], reverse=True)[:5]
        ]

        payout_statuses = {r.get("payout_status", "not_ready") for r in reservations_data}
        if not payout_statuses or payout_statuses == {"not_ready"}:
            aggregate_payout_status = "not_ready"
        elif len(payout_statuses) == 1:
            aggregate_payout_status = next(iter(payout_statuses))
        else:
            aggregate_payout_status = "mixed"

        return {
            "periode": periode,
            "total_gains_bruts_mad": round(total_brut, 2),
            "total_commissions_plateforme_mad": round(total_commission, 2),
            "total_gains_nets_mad": round(gains_nets, 2),
            "total_cautions_restituees_mad": round(released_deposits_mad, 2),
            "nombre_locations_terminees": completed_count,
            "taux_occupation_pct": 0.0,
            "top_articles_rentables": top_articles,
            "payout_pending_mad": round(pending_payout, 2),
            "payout_status": aggregate_payout_status,
        }

earnings_service = EarningsService()
