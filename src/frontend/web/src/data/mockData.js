export const MOROCCAN_CITIES = [
  'Toutes les villes',
  'Casablanca',
  'Rabat',
  'Marrakech',
  'Tanger',
  'Fès',
  'Agadir',
  'Oujda'
];

export const CATEGORIES = [
  { id: 'all', label: 'Toutes les catégories', icon: 'Layers' },
  { id: 'outils', label: 'Outils & Bricolage', icon: 'Wrench', description: 'Perforateurs, scies, échafaudages, ponceuses' },
  { id: 'electronique', label: 'Électronique & Vidéo', icon: 'Camera', description: 'Caméras 4K, drones, éclairage LED, objectifs' },
  { id: 'musique', label: 'Instruments de musique', icon: 'Music', description: 'Guitares, claviers, micros, amplis' },
  { id: 'evenementiel', label: 'Fête & Événementiel', icon: 'Sparkles', description: 'Enceintes sono, chapiteaux, tireuses, lumières' },
  { id: 'outdoor', label: 'Outdoor & Camping', icon: 'Compass', description: 'Tentes de toit, paddles, matériel de bivouac' },
  { id: 'velos', label: 'Remorques & Vélos', icon: 'Bike', description: 'Remorques porte-motos, vélos électriques' },
];

export const INITIAL_EQUIPMENT = [
  {
    id: 'e1111111-1111-1111-1111-111111111111',
    title: 'Perforateur Burineur Démolition Pro SDS-Max 1500W',
    description: 'Marteau piqueur démolition professionnel Bosch 1500W, force de frappe 25 Joules. 4 burins fournis avec coffret.',
    category: 'outils',
    city: 'Casablanca',
    address: 'Ain Sebaa, Casablanca',
    daily_price_mad: 120,
    deposit_amount_mad: 1000,
    is_available: true,
    is_verified: true,
    discount_pct: 15,
    rating: 4.95,
    reviews_count: 34,
    owner_name: 'Atlas Location BTP Maroc',
    is_pro: true,
    specs: { 'Puissance': '1500W', 'Impact': '25 Joules', 'Emmanchement': 'SDS-Max' },
    image: '/images/jackhammer.jpg'
  },
  {
    id: 'e2222222-2222-2222-2222-222222222222',
    title: 'Pack Caméra Cinéma Sony FX3 Full-Frame 4K + Cage XLR',
    description: 'Boîtier cinéma plein format Sony FX3, 2 cartes CFexpress 160Go, 4 batteries, poignée son XLR, objectif 24-70mm f/2.8 GM.',
    category: 'electronique',
    city: 'Marrakech',
    address: 'Guéliz, Marrakech',
    daily_price_mad: 450,
    deposit_amount_mad: 5000,
    is_available: true,
    is_verified: true,
    discount_pct: 10,
    rating: 5.0,
    reviews_count: 19,
    owner_name: 'Red City Prod Marrakech',
    is_pro: true,
    specs: { 'Résolution': '4K 120fps', 'Capteur': 'Plein Format 12.1 MP', 'Son': 'XLR 4 Canaux' },
    image: '/images/sony_fx3.jpg'
  },
  {
    id: 'e3333333-3333-3333-3333-333333333333',
    title: 'Guitare Électro-Acoustique Fender CD-60SCE + Ampli Fishman',
    description: 'Table en épicéa massif, pan coupé, micro et préampli Fishman intégrés avec accordeur. Housse et câble jack inclus.',
    category: 'musique',
    city: 'Rabat',
    address: 'Agdal, Rabat',
    daily_price_mad: 90,
    deposit_amount_mad: 800,
    is_available: true,
    is_verified: true,
    discount_pct: 0,
    rating: 4.9,
    reviews_count: 12,
    owner_name: 'Youssef Berrada',
    is_pro: false,
    specs: { 'Marque': 'Fender', 'Préampli': 'Fishman Classic', 'Accessoires': 'Housse + Câble' },
    image: '/images/guitar_fender.jpg'
  },
  {
    id: 'e4444444-4444-4444-4444-444444444444',
    title: 'Pack Sonorisation JBL PartyBox 710 (800W RMS) + 2 Micros',
    description: 'Enceinte de soirée ultra-puissante 800W avec jeux de lumières dynamiques synchronisés, entrées guitare et micros sans fil.',
    category: 'evenementiel',
    city: 'Casablanca',
    address: 'Maârif, Casablanca',
    daily_price_mad: 250,
    deposit_amount_mad: 2000,
    is_available: true,
    is_verified: true,
    discount_pct: 5,
    rating: 4.92,
    reviews_count: 27,
    owner_name: 'Atlas Location BTP Maroc',
    is_pro: true,
    specs: { 'Puissance': '800W RMS', 'Lumières': 'RGB Dynamiques', 'Micros': '2 UHF Sans Fil' },
    image: '/images/partybox.jpg'
  },
  {
    id: 'e5555555-5555-5555-5555-555555555555',
    title: 'Tente de Toit Voiture 4 Saisons 2/3 Personnes Hussarde',
    description: 'Tente de toit rigide ouverture rapide 30s, matelas haute densité mémoire de forme, échelle télescopique alu incluse.',
    category: 'outdoor',
    city: 'Casablanca',
    address: 'Bourgogne, Casablanca',
    daily_price_mad: 180,
    deposit_amount_mad: 1500,
    is_available: true,
    is_verified: true,
    discount_pct: 0,
    rating: 4.85,
    reviews_count: 16,
    owner_name: 'Karim Tazi',
    is_pro: false,
    specs: { 'Capacité': '2-3 Personnes', 'Matelas': '140 x 200 cm', 'Ouverture': 'Hydraulique 30s' },
    image: '/images/roof_tent.jpg'
  },
  {
    id: 'e6666666-6666-6666-6666-666666666666',
    title: 'Remorque Porte-Motos / Porte-Vélos Basculante 500kg',
    description: 'Remorque galvanisée homologuée route avec rampe de montée, antivol tête d attelage et roue jockey.',
    category: 'velos',
    city: 'Casablanca',
    address: 'Sidi Maarouf, Casablanca',
    daily_price_mad: 140,
    deposit_amount_mad: 1200,
    is_available: true,
    is_verified: true,
    discount_pct: 0,
    rating: 4.95,
    reviews_count: 31,
    owner_name: 'Atlas Location BTP Maroc',
    is_pro: true,
    specs: { 'Charge Utile': '500 kg', 'Prise': '7 broches', 'Rampe': 'Fournie' },
    image: '/images/trailer_500kg.jpg'
  }
];

export const HOW_IT_WORKS_STEPS = [
  {
    step: '01',
    title: 'Trouvez le matériel idéal',
    description: 'Parcourez les annonces vérifiées près de chez vous à Casablanca, Rabat, Marrakech et partout au Maroc.'
  },
  {
    step: '02',
    title: 'Réservez en Cash on Delivery (COD)',
    description: 'Sélectionnez vos dates. Aucun paiement bancaire en ligne requis. Réglez le montant et la caution en cash à la remise.'
  },
  {
    step: '03',
    title: 'État des lieux scellé & Vérification Didit',
    description: 'Contrôle d identité biométrique Didit et photos contradictoires horodatées au retrait et au retour.'
  }
];
