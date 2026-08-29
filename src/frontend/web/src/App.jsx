import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import EquipmentGrid from './components/EquipmentGrid';
import EquipmentModal from './components/EquipmentModal';
import OwnerDashboard from './components/OwnerDashboard';
import KYCVerificationModal from './components/KYCVerificationModal';
import AddEquipmentModal from './components/AddEquipmentModal';
import InspectionModal from './components/InspectionModal';
import ContractViewerModal from './components/ContractViewerModal';
import AuthModal from './components/AuthModal';
import GeoCitiesSection from './components/GeoCitiesSection';
import PricingSection from './components/PricingSection';
import FAQSection from './components/FAQSection';
import { INITIAL_EQUIPMENT } from './data/mockData';
import { getEquipmentList, getCurrentUser } from './services/api';
import { subscribeToAuthState, logoutUser } from './services/firebase';
import { ShieldCheck, Lock, FileText, PhoneCall } from 'lucide-react';

export default function App() {
  const [currentView, setCurrentView] = useState('catalog'); // 'catalog' | 'dashboard'
  const [selectedCity, setSelectedCity] = useState('Toutes les villes');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  
  const [equipmentList, setEquipmentList] = useState(INITIAL_EQUIPMENT);
  const [selectedEquipment, setSelectedEquipment] = useState(null);
  const [equipmentModalMode, setEquipmentModalMode] = useState('details');
  
  // User Session & KYC
  const [currentUser, setCurrentUser] = useState(() => {
    const saved = typeof localStorage !== 'undefined' ? localStorage.getItem('lokiini_user') : null;
    return saved ? JSON.parse(saved) : null;
  });
  const [isKYCVerified, setIsKYCVerified] = useState(() => {
    const saved = typeof localStorage !== 'undefined' ? localStorage.getItem('lokiini_user') : null;
    if (!saved) return false;
    try {
      const parsed = JSON.parse(saved);
      return Boolean(parsed.is_kyc_verified);
    } catch {
      return false;
    }
  });

  // Modals visibility states
  const [isKYCModalOpen, setIsKYCModalOpen] = useState(false);
  const [isAddEquipmentOpen, setIsAddEquipmentOpen] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  
  // Contract Viewer Modal
  const [viewingContractBookingId, setViewingContractBookingId] = useState(null);
  const [viewingContractData, setViewingContractData] = useState(null);

  // Inspection Modal
  const [inspectionModalData, setInspectionModalData] = useState(null);
  const [inspectionType, setInspectionType] = useState('check_in');

  // Fetch from FastAPI backend with fallback
  const loadCatalogue = async () => {
    const apiData = await getEquipmentList({
      city: selectedCity,
      category: selectedCategory,
      search: searchTerm
    });
    if (apiData && apiData.length > 0) {
      const mapped = apiData.map(item => ({
        ...item,
        rating: item.rating || 4.9,
        reviews_count: item.reviews_count || 15,
        image: item.images_urls?.[0] || 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?w=800',
        specs: item.specs_json || item.specs || {}
      }));
      setEquipmentList(mapped);
    } else {
      // Local filtered fallback
      const local = INITIAL_EQUIPMENT.filter((item) => {
        const matchCity = selectedCity === 'Toutes les villes' || item.city.toLowerCase() === selectedCity.toLowerCase();
        const matchCategory = selectedCategory === 'all' || item.category === selectedCategory;
        const matchSearch = searchTerm === '' || item.title.toLowerCase().includes(searchTerm.toLowerCase()) || item.description.toLowerCase().includes(searchTerm.toLowerCase());
        return matchCity && matchCategory && matchSearch;
      });
      setEquipmentList(local);
    }
  };

  useEffect(() => {
    loadCatalogue();
  }, [selectedCity, selectedCategory, searchTerm]);

  const handleSelectEquipment = (item, mode) => {
    setSelectedEquipment(item);
    setEquipmentModalMode(mode);
  };

  const handleEquipmentAdded = (newItem) => {
    setEquipmentList(prev => [newItem, ...prev]);
  };

  const handleOpenContract = (bookingId, bookingData) => {
    setViewingContractBookingId(bookingId);
    setViewingContractData(bookingData);
  };

  const handleOpenInspection = (bookingData, type) => {
    setInspectionModalData(bookingData);
    setInspectionType(type);
  };

  // Listen to Firebase authentication state
  useEffect(() => {
    const unsubscribe = subscribeToAuthState((user) => {
      if (user) {
        setCurrentUser(user);
      }
    });
    return () => {
      if (typeof unsubscribe === 'function') unsubscribe();
    };
  }, []);

  const handleLogout = async () => {
    await logoutUser();
    setCurrentUser(null);
  };

  // Dynamic SEO & GEO Page Metadata
  useEffect(() => {
    let title = "Lokiini — N°1 Location de Tout Matériel & Équipements au Maroc";
    if (selectedCity && selectedCity !== 'Toutes les villes') {
      title = `Location de Matériel & Équipements à ${selectedCity} — Lokiini Maroc`;
    }
    if (selectedCategory && selectedCategory !== 'all') {
      const catNames = {
        'event': 'Matériel Événementiel & Fêtes',
        'audiovisual': 'Matériel Audiovisuel, Photo & Drones',
        'tools': 'Bricolage, Outillage & Jardin',
        'btp': 'BTP, Chantier & Gros Œuvre',
        'energy': 'Groupes Électrogènes & Énergie',
        'vehicles': 'Véhicules, Remorques & Loisirs',
        'hightech': 'High-Tech, Gaming & Informatique',
        'medical': 'Matériel Médical & Soins'
      };
      title = `Location ${catNames[selectedCategory] || 'Matériel'} au Maroc — Lokiini`;
    }
    document.title = title;
  }, [selectedCity, selectedCategory]);

  return (
    <div className="min-h-screen flex flex-col bg-lokiini-sand">
      
      {/* 1. Header Navigation */}
      <Navbar
        currentView={currentView}
        setCurrentView={setCurrentView}
        isKYCVerified={isKYCVerified}
        onOpenKYC={() => setIsKYCModalOpen(true)}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onOpenAddEquipment={() => setIsAddEquipmentOpen(true)}
        currentUser={currentUser}
        onLogout={handleLogout}
      />

      {/* 2. Main Body View */}
      <main className="flex-1">
        {currentView === 'catalog' ? (
          <>
            {/* Hero & Search Bar */}
            <Hero
              selectedCity={selectedCity}
              setSelectedCity={setSelectedCity}
              selectedCategory={selectedCategory}
              setSelectedCategory={setSelectedCategory}
              searchTerm={searchTerm}
              setSearchTerm={setSearchTerm}
            />

            {/* Equipment Grid */}
            <EquipmentGrid
              equipmentList={equipmentList}
              onSelectEquipment={handleSelectEquipment}
            />

            {/* Moroccan Regional Hubs (GEO Targeting) */}
            <GeoCitiesSection
              selectedCity={selectedCity}
              onSelectCity={(city) => {
                setSelectedCity(city);
                window.scrollTo({ top: 380, behavior: 'smooth' });
              }}
            />

            {/* Subscription & Pricing Plans */}
            <PricingSection
              onSelectPlan={(planId) => {
                if (currentUser) {
                  setCurrentView('dashboard');
                } else {
                  setIsAuthModalOpen(true);
                }
              }}
              onOpenAuth={() => setIsAuthModalOpen(true)}
            />

            {/* GEO Generative Engine Optimization & FAQ */}
            <FAQSection />
          </>
        ) : currentView === 'pricing' ? (
          /* Dedicated Pricing View */
          <div className="py-8 bg-stone-50 min-h-[80vh]">
            <PricingSection
              onSelectPlan={(planId) => {
                if (currentUser) {
                  setCurrentView('dashboard');
                } else {
                  setIsAuthModalOpen(true);
                }
              }}
              onOpenAuth={() => setIsAuthModalOpen(true)}
            />
            <FAQSection />
          </div>
        ) : currentUser ? (
          /* Pro Loueur Dashboard */
          <OwnerDashboard
            onNewEquipment={() => setIsAddEquipmentOpen(true)}
            onOpenContract={handleOpenContract}
            onOpenInspection={handleOpenInspection}
            currentUser={currentUser}
          />
        ) : (
          /* Non-authenticated Dashboard Gate */
          <div className="py-16 bg-stone-50 min-h-[70vh] flex items-center justify-center px-4">
            <div className="bg-white rounded-3xl p-8 max-w-lg w-full text-center border border-stone-200 shadow-xl space-y-5">
              <div className="w-16 h-16 bg-emerald-50 text-lokiini-teal rounded-2xl flex items-center justify-center mx-auto shadow-inner">
                <Lock className="w-8 h-8" />
              </div>
              <h2 className="text-2xl font-black text-lokiini-charcoal font-['Outfit']">
                Espace Réservé aux Loueurs Pro
              </h2>
              <p className="text-xs text-stone-500 leading-relaxed">
                Connectez-vous avec votre compte Firebase ou créez un compte Loueur Professionnel pour gérer votre matériel en location (événementiel, audiovisuel, outillage, high-tech, véhicules, BTP), suivre les baux DOC et vos cautions CMI.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <button
                  onClick={() => setIsAuthModalOpen(true)}
                  className="flex-1 bg-lokiini-teal hover:bg-lokiini-teal-dark text-white font-bold py-3 px-4 rounded-xl text-xs transition-all shadow"
                >
                  Se Connecter avec Firebase
                </button>
                <button
                  onClick={() => setCurrentView('pricing')}
                  className="flex-1 bg-stone-100 hover:bg-stone-200 text-stone-700 font-bold py-3 px-4 rounded-xl text-xs transition-all border border-stone-200"
                >
                  Voir la Grille Tarifaire
                </button>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* 3. Footer with Moroccan Legal & Trust Footprint */}
      <footer className="bg-lokiini-charcoal text-stone-400 text-xs py-12 border-t border-stone-800">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center gap-2 mb-3">
              <div className="bg-white/95 p-1 rounded-lg border border-stone-700">
                <img src="/logo.png" alt="Lokiini Logo" className="h-7 w-auto object-contain" />
              </div>
            </div>
            <p className="text-stone-400 text-xs leading-relaxed">
              Plateforme universelle de location de matériel et d'équipements de confiance au Royaume du Maroc.
            </p>
          </div>

          <div>
            <h4 className="text-white font-bold mb-3">Conformité Marocaine</h4>
            <ul className="space-y-2 text-stone-400">
              <li className="flex items-center gap-1.5"><ShieldCheck className="w-3.5 h-3.5 text-lokiini-teal" /> CNDP (Loi n° 09-08)</li>
              <li className="flex items-center gap-1.5"><FileText className="w-3.5 h-3.5 text-lokiini-teal" /> Contrats DOC (Art. 627+)</li>
              <li className="flex items-center gap-1.5"><Lock className="w-3.5 h-3.5 text-lokiini-teal" /> Signature Loi n° 53-05</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-bold mb-3">Paiement & Cautions</h4>
            <ul className="space-y-2 text-stone-400">
              <li>Passerelle CMI / Payzone 3D-Secure</li>
              <li>Réseau CashPlus / Wafacash</li>
              <li>Caution séquestrée non débitée</li>
            </ul>
          </div>

          <div>
            <h4 className="text-white font-bold mb-3">Assistance & Contact</h4>
            <p className="text-stone-400 mb-2">Conseiller WhatsApp 7j/7 pour artisans et professionnels au Maroc.</p>
            <div className="flex items-center gap-2 text-lokiini-teal font-bold">
              <PhoneCall className="w-4 h-4" />
              <span>+212 5 22 00 00 00</span>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6 border-t border-stone-800 text-center text-stone-500">
          © {new Date().getFullYear()} Lokiini Maroc. Tous droits réservés. Architecture 100% Conteneurisée Docker.
        </div>
      </footer>

      {/* 4. Equipment Details & Booking Modal */}
      {selectedEquipment && (
        <EquipmentModal
          equipment={selectedEquipment}
          initialMode={equipmentModalMode}
          isKYCVerified={isKYCVerified}
          onOpenKYC={() => setIsKYCModalOpen(true)}
          onClose={() => setSelectedEquipment(null)}
          onBookingSuccess={() => loadCatalogue()}
          onOpenContract={handleOpenContract}
          onOpenInspection={handleOpenInspection}
        />
      )}

      {/* 5. KYC Verification Modal */}
      <KYCVerificationModal
        isOpen={isKYCModalOpen}
        onClose={() => setIsKYCModalOpen(false)}
        onVerificationSuccess={() => setIsKYCVerified(true)}
      />

      {/* 6. Add Equipment Modal (Pro Owner) */}
      <AddEquipmentModal
        isOpen={isAddEquipmentOpen}
        onClose={() => setIsAddEquipmentOpen(false)}
        onEquipmentAdded={handleEquipmentAdded}
      />

      {/* 7. Contradictory Inspection Modal */}
      {inspectionModalData && (
        <InspectionModal
          isOpen={!!inspectionModalData}
          onClose={() => setInspectionModalData(null)}
          booking={inspectionModalData}
          type={inspectionType}
          onInspectionSuccess={() => loadCatalogue()}
        />
      )}

      {/* 8. DOC Lease Contract Viewer Modal */}
      {viewingContractBookingId && (
        <ContractViewerModal
          isOpen={!!viewingContractBookingId}
          onClose={() => setViewingContractBookingId(null)}
          bookingId={viewingContractBookingId}
          bookingData={viewingContractData}
        />
      )}

      {/* 9. Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={(user) => setCurrentUser(user)}
      />

    </div>
  );
}
