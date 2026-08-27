# Spécifications Techniques — Module Biométrique & Vision IA

## 1. Pipeline de Détection Anti-Spoofing & Liveness (ISO/IEC 30107-3)
- **Niveau 1 (Présentation 2D)** : Rejet des photos imprimées, des écrans smartphones et tablettes via transformée de Fourier 2D (FFT) analysant les fréquences spatiales et les reflets du moiré d'affichage.
- **Niveau 2 (Présentation 3D & Rejeu Dynamique)** : Défi cinématique aléatoire (Face Landmark 468 points MediaPipe) mesurant la rotation 3D de la boîte englobante de la tête ($\Delta 	heta_y \ge 15^\circ$) et la cinématique palpébrale (clignement d'yeux naturel avec ratio EAR - Eye Aspect Ratio $< 0.2$).
- **Niveau 3 (Anti-Deepfake Spectrale)** : Extraction des artefacts de synthèse dans le domaine résiduel chromatique (YUV/HSV) et vérification de la concordance de phase lumineuse cornéenne.

## 2. Inférence & Empreintes Zero-Knowledge
- Modèle d'Embedding : ArcFace / MobileFaceNet (Vecteur 512-D normalisé $).
- Seuil de décision : $	ext{Similarité Cosinus} \ge 0.78$ ( < 0.001\%$,  < 0.8\%$).
- Éphémérité : Flux vidéo traité en RAM volatile dans un conteneur chiffré (	mpfs) et détruit immédiatement après extraction vectorielle.
