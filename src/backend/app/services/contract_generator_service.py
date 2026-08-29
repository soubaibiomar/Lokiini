import hashlib
from datetime import datetime
from typing import Dict, Any

class ContractGeneratorService:
    @classmethod
    def generate_lease_contract(
        cls,
        booking_data: Dict[str, Any],
        article_data: Dict[str, Any],
        renter_data: Dict[str, Any],
        owner_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Génère le texte complet du bail de location conforme aux Articles 627+ du DOC Maroc."""
        contract_number = f"BAIL-LOKIINI-{str(booking_data['id'])[:8].upper()}-{datetime.utcnow().year}"
        
        owner_id_info = owner_data.get('company_ice') if owner_data.get('company_ice') else (owner_data.get('cin_number') or 'CIN Certifiée Didit')
        renter_id_info = renter_data.get('company_ice') if renter_data.get('company_ice') else (renter_data.get('cin_number') or 'CIN Certifiée Didit')

        contract_text = f"""
================================================================================
CONTRAT DE LOCATION DE BIENS MOBILIERS ET D'ÉQUIPEMENTS
Régit par les Articles 627 et suivants du Dahir formant Code des Obligations et des Contrats (DOC Maroc)
Référence Contrat : {contract_number}
================================================================================

ENTRE LES SOUSSIGNÉS :

1. LE BAILLEUR (Loueur) :
- Nom & Prénom / Raison Sociale : {owner_data.get('nom_complet', 'Loueur Lokiini')}
- CIN / ICE : {owner_id_info}
- Téléphone : {owner_data.get('telephone', '+212600000000')}
- Ville : {owner_data.get('city', 'Casablanca')}

ET

2. LE PRENEUR (Locataire) :
- Nom & Prénom / Raison Sociale : {renter_data.get('nom_complet', 'Locataire Lokiini')}
- CIN / ICE : {renter_id_info}
- Téléphone : {renter_data.get('telephone', '+212600000000')}
- Ville : {renter_data.get('city', 'Casablanca')}

IL A ÉTÉ CONVENU ET ARRÊTÉ CE QUI SUIT :

ARTICLE 1 - OBJET DU CONTRAT (Art. 627 DOC)
Le Bailleur donne en location au Preneur, qui accepte, le matériel désigné ci-après :
- Désignation : {article_data.get('titre')}
- Catégorie : {article_data.get('categorie')}
- Description : {article_data.get('description')}

ARTICLE 2 - DURÉE DE LA LOCATION
La présente location est consentie pour une durée ferme de {booking_data.get('nombre_jours', 1)} jour(s),
prenant effet le {booking_data.get('date_debut')} et expirant le {booking_data.get('date_fin')}.

ARTICLE 3 - CONDITIONS FINANCIÈRES (PRIX ET PAIEMENT)
- Loyer Total : {booking_data.get('prix_total')} MAD
- Mode de Paiement : Cash on Delivery (COD) à la remise
- Dépôt de Garantie (Caution) : {booking_data.get('montant_caution')} MAD (Remise en espèces à la livraison)

ARTICLE 4 - OBLIGATIONS DU PRENEUR ET ÉTAT DES LIEUX (Art. 675 & 676 DOC)
Le Preneur s'engage à user du bien loué en bon père de famille et conformément à sa destination.
Un état des lieux contradictoire horodaté et scellé par empreinte cryptographique SHA-256 (RFC 3161)
est dressé au moment du retrait et du retour.

ARTICLE 5 - INTERDICTION DE SOUS-LOCATION (Art. 668 DOC)
Toute sous-location ou cession du présent bail est strictement interdite sans accord écrit du Bailleur.

ARTICLE 6 - LOI APPLICABLE ET ATTRIBUTION DE JURIDICTION
Le présent contrat est soumis au droit marocain (Dahir des Obligations et Contrats).
En cas de litige relatif à l'interprétation ou l'exécution du contrat, compétence expresse est attribuée
aux juridictions compétentes du Royaume du Maroc.

Fait sous forme électronique certifiée conforme à la Loi n° 53-05 relative à l'échange électronique de données juridiques.
        """.strip()

        contract_hash = hashlib.sha256(contract_text.encode("utf-8")).hexdigest()

        return {
            "contract_number": contract_number,
            "contract_text": contract_text,
            "contract_sha256": contract_hash,
            "applicable_law": "DOC Maroc (Art. 627+) & Loi 53-05",
            "generated_at": datetime.utcnow()
        }

contract_generator_service = ContractGeneratorService()
