# Dossier de Déclaration Préalable CNDP — Canevas Officiel (Loi 09-08)

## 1. Identification du Responsable de Traitement
- **Raison Sociale** : MatOS SARL-AU
- **Siège Social** : Casablanca, Maroc
- **Représentant Légal** : Gérant Associé Unique
- **Délégué à la Protection des Données (DPO)** : contact-dpo@matos.ma

## 2. Finalités du Traitement
- Vérification d'identité des utilisateurs pour la prévention de la fraude, de l'usurpation d'identité et du vol de matériel loué.
- Établissement de contrats de location électroniques conformes au Dahir des Obligations et Contrats (DOC).
- Sécurisation des transactions financières et conformité bancaire (Anti-Blanchiment / KYC).

## 3. Catégories de Données Collectées
- **Données d'état civil** : Nom, prénom, date de naissance, adresse postale, numéro de CIN/Passeport.
- **Données d'authentification biométrique** : Vecteur mathématique d'empreinte faciale (512 dimensions normalisé), score de liveness check. *Remarque : aucun flux vidéo brut n'est enregistré ni stocké.*
- **Données techniques et de géolocalisation** : Horodatage UTC certifié (RFC 3161), coordonnées GPS au moment de l'état des lieux contradictoire.

## 4. Mesures de Sécurité & Confidentialité
- Chiffrement symétrique AES-256-GCM au repos pour l'ensemble des documents d'identité.
- Chiffrement TLS 1.3 en transit.
- Purge instantanée en RAM des flux de webcam/caméra après calcul de l'empreinte vectorielle.
- Journalisation d'accès avec traçabilité d'audit immuable.
