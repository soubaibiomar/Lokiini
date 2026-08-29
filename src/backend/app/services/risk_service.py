from typing import Dict, Any, Optional

class RiskService:
    HIGH_RISK_CATEGORIES = ["btp", "audiovisuel", "energy", "cameras_pro", "heavy_machinery"]

    @classmethod
    def evaluate_risk(
        cls, 
        categorie: str, 
        prix_par_jour: float, 
        montant_caution: float,
        specs: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Détermine le niveau de risque d'un article et les exigences associées :
        - faible : Matériel standard < 500 MAD de caution et < 150 MAD/jour (KYC optionnel)
        - moyen  : Matériel de 500 à 3 000 MAD de caution ou 150-500 MAD/jour (KYC Didit obligatoire)
        - eleve  : Matériel lourd > 3 000 MAD de caution, > 500 MAD/jour ou BTP/Audiovisuel (KYC + Caution cash)
        """
        cat_lower = (categorie or "").lower().strip()
        caution = float(montant_caution or 0.0)
        daily = float(prix_par_jour or 0.0)
        
        # 1. Critères de risque Élevé
        if caution >= 3000.0 or daily >= 500.0 or cat_lower in cls.HIGH_RISK_CATEGORIES:
            return {
                "niveau_risque": "eleve",
                "kyc_obligatoire": True,
                "caution_obligatoire": True,
                "label": "🔴 Matériel à Haute Valeur (KYC & Caution obligatoires)"
            }
        
        # 2. Critères de risque Moyen
        elif caution >= 500.0 or daily >= 150.0:
            return {
                "niveau_risque": "moyen",
                "kyc_obligatoire": True,
                "caution_obligatoire": False,
                "label": "🟡 Risque Moyen (Vérification d'identité Didit requise)"
            }
            
        # 3. Risque Faible
        else:
            return {
                "niveau_risque": "faible",
                "kyc_obligatoire": False,
                "caution_obligatoire": False,
                "label": "🟢 Risque Faible (Accès libre)"
            }

risk_service = RiskService()
