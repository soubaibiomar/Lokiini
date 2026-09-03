import hashlib
from datetime import datetime
from typing import Any, Dict


PAYMENT_METHOD_LABELS = {
    "cash_cod": "Paiement en espèces à la remise",
    "cash_on_delivery": "Paiement en espèces à la remise",
    "cmi_card": "Paiement par carte via le prestataire configuré",
    "cmi": "Paiement par carte via le prestataire configuré",
    "cashplus": "Paiement via le réseau indiqué dans la réservation",
}

DEPOSIT_METHOD_LABELS = {
    "cash": "Dépôt remis en espèces selon les modalités convenues",
    "authorization": "Autorisation de dépôt auprès du prestataire configuré",
}


class ContractGeneratorService:
    @classmethod
    def generate_lease_contract(
        cls,
        booking_data: Dict[str, Any],
        article_data: Dict[str, Any],
        renter_data: Dict[str, Any],
        owner_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate the French contract text from authoritative reservation data."""
        contract_number = f"BAIL-LOKIINI-{str(booking_data['id'])[:8].upper()}-{datetime.utcnow().year}"

        owner_id_info = owner_data.get("company_ice") or owner_data.get("cin_number") or "Non renseigné"
        renter_id_info = renter_data.get("company_ice") or renter_data.get("cin_number") or "Non renseigné"
        payment_method = PAYMENT_METHOD_LABELS.get(
            booking_data.get("payment_method"), "Modalité indiquée dans la réservation"
        )
        deposit_method = DEPOSIT_METHOD_LABELS.get(
            booking_data.get("deposit_method"), "Modalité indiquée dans la réservation"
        )

        responsibilities = [
            "Le propriétaire remet le matériel dans l’état et avec les éléments décrits dans le contrat.",
            "Le locataire utilise le matériel conformément à sa destination et aux règles communiquées.",
            "Les deux parties vérifient ensemble l’état du matériel lors de la remise et du retour.",
            "Le locataire restitue le matériel à la date prévue, sous réserve d’un accord différent enregistré entre les parties.",
        ]
        important_conditions = [
            "La période, le prix de location et le dépôt sont ceux enregistrés dans la réservation confirmée.",
            "Toute sous-location ou cession nécessite l’accord écrit du propriétaire.",
            "Un désaccord sur l’état du matériel peut être traité à partir des éléments enregistrés lors des inspections.",
            "Ce document généré ne constitue pas un certificat de signature électronique qualifiée.",
        ]

        contract_text = f"""
CONTRAT DE LOCATION DE BIENS MOBILIERS ET D'ÉQUIPEMENTS
Référence : {contract_number}
Langue : français

PARTIES

PROPRIÉTAIRE
- Nom / raison sociale : {owner_data.get('nom_complet') or 'Non renseigné'}
- CIN / ICE : {owner_id_info}
- Téléphone : {owner_data.get('telephone') or 'Non renseigné'}
- Ville : {owner_data.get('city') or 'Non renseignée'}

LOCATAIRE
- Nom / raison sociale : {renter_data.get('nom_complet') or 'Non renseigné'}
- CIN / ICE : {renter_id_info}
- Téléphone : {renter_data.get('telephone') or 'Non renseigné'}
- Ville : {renter_data.get('city') or 'Non renseignée'}

MATÉRIEL
- Désignation : {article_data.get('titre') or 'Matériel'}
- Catégorie : {article_data.get('categorie') or 'Non renseignée'}
- Description : {article_data.get('description') or 'Non renseignée'}

PÉRIODE
- Début : {booking_data.get('date_debut')}
- Fin : {booking_data.get('date_fin')}
- Durée enregistrée : {booking_data.get('nombre_jours')} jour(s)

CONDITIONS FINANCIÈRES
- Prix total de location : {booking_data.get('prix_total')} MAD
- Modalité de paiement : {payment_method}
- Dépôt de garantie : {booking_data.get('montant_caution')} MAD
- Modalité du dépôt : {deposit_method}

RESPONSABILITÉS
{chr(10).join(f'- {item}' for item in responsibilities)}

CONDITIONS IMPORTANTES
{chr(10).join(f'- {item}' for item in important_conditions)}

DROIT APPLICABLE
Le contrat se réfère au droit marocain et notamment aux dispositions applicables du Dahir formant Code des obligations et des contrats. En cas de désaccord, les parties conservent les recours prévus par le droit applicable.

Document généré électroniquement par Lokiini à partir des informations de la réservation confirmée. La génération et l'empreinte SHA-256 du contenu ne valent pas, à elles seules, signature électronique qualifiée ni certificat de signature.
        """.strip()

        contract_hash = hashlib.sha256(contract_text.encode("utf-8")).hexdigest()

        return {
            "contract_number": contract_number,
            "contract_text": contract_text,
            "contract_sha256": contract_hash,
            "applicable_law": "Droit marocain — référence au DOC",
            "generated_at": datetime.utcnow(),
            "language": "fr",
            "available_languages": ["fr"],
            "responsibilities": responsibilities,
            "important_conditions": important_conditions,
            "payment_method_label": payment_method,
            "deposit_method_label": deposit_method,
        }


contract_generator_service = ContractGeneratorService()
