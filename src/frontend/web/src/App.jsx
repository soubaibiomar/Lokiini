import React, { useCallback, useRef, useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import { HowLokiiniWorks, OwnerCallToAction, TrustSafetySection } from './components/HomeSections';
import CatalogueExperience from './components/CatalogueExperience';
import EquipmentModal from './components/EquipmentModal';
import AccountDashboard from './components/AccountDashboard';
import KYCVerificationModal from './components/KYCVerificationModal';
import AddEquipmentModal from './components/AddEquipmentModal';
import InspectionModal from './components/InspectionModal';
import ContractViewerModal from './components/ContractViewerModal';
import AuthModal from './components/AuthModal';
import GeoCitiesSection from './components/GeoCitiesSection';
import PricingSection from './components/PricingSection';
import FAQSection from './components/FAQSection';
import { Footer, Container, PageShell } from './components/layout';
import { Breadcrumb, Button, Card } from './components/ui';
import { getEquipmentCategories, getEquipmentPage } from './services/api';
import { subscribeToAuthState, logoutUser } from './services/firebase';
import { Lock } from 'lucide-react';
import { useI18n } from './i18n';

const CATEGORY_LABELS = {
  tools: 'Outils & bricolage',
  btp: 'BTP & chantier',
  audiovisual: 'Photo & audiovisuel',
  audiovisuel: 'Photo & audiovisuel',
  event: 'Événementiel',
  evenementiel: 'Événementiel',
  outdoor: 'Plein air & camping',
  cleaning: 'Nettoyage & entretien',
  energy: 'Énergie',
  transport: 'Transport',
  vehicles: 'Véhicules',
  hightech: 'High-tech',
  medical: 'Matériel médical',
};

const categoryLabel = (category) => CATEGORY_LABELS[category] || category.replaceAll('_', ' ').replace(/^./, (letter) => letter.toUpperCase());

const PAGE_SIZE = 12;

function readCatalogueFilters() {
  const params = new URLSearchParams(window.location.search);
  const numberOrNull = (key) => {
    const value = params.get(key);
    if (value === null || value === '') return null;
    const parsed = Number(value);
    return Number.isFinite(parsed) && parsed >= 0 ? parsed : null;
  };
  return {
    search: params.get('q') || '',
    category: params.get('category') || 'all',
    city: params.get('city') || 'Toutes les villes',
    prix_min: numberOrNull('min_price'),
    prix_max: numberOrNull('max_price'),
    verified: params.get('verified') === 'true',
    available: params.get('available') !== 'false',
    radius: numberOrNull('radius') || 25,
    position: null,
  };
}

function catalogueErrorMessage(error) {
  if (error?.status === 502 || error?.status === 503 || error?.status === 504 || error?.code === 'NETWORK_ERROR') {
    return 'Le catalogue est temporairement indisponible. Réessayez dans quelques instants.';
  }
  if (error?.code === 'REQUEST_TIMEOUT') {
    return 'Le catalogue met trop de temps à répondre. Vérifiez votre connexion puis réessayez.';
  }
  return error?.message || 'Impossible de charger le catalogue.';
}

export default function App() {
  const { t } = useI18n();
  const [currentView, setCurrentView] = useState(() => (
    window.location.hash.startsWith('#account-') ? 'dashboard' : 'catalog'
  )); // 'catalog' | 'dashboard' | 'pricing'
  const [catalogueFilters, setCatalogueFilters] = useState(readCatalogueFilters);
  
  const [equipmentList, setEquipmentList] = useState([]);
  const [catalogueLoading, setCatalogueLoading] = useState(true);
  const [catalogueLoadingMore, setCatalogueLoadingMore] = useState(false);
  const [catalogueTotal, setCatalogueTotal] = useState(null);
  const [catalogueHasMore, setCatalogueHasMore] = useState(false);
  const [homepageCategories, setHomepageCategories] = useState([]);
  const [homepageCities, setHomepageCities] = useState([]);
  const [catalogueError, setCatalogueError] = useState(null);
  const catalogueRequestRef = useRef(0);
  const [selectedEquipment, setSelectedEquipment] = useState(null);
  const [equipmentModalMode, setEquipmentModalMode] = useState('details');
  
  // User Session & KYC
  const [currentUser, setCurrentUser] = useState(null);
  const [isKYCVerified, setIsKYCVerified] = useState(false);
  const [sessionError, setSessionError] = useState(null);

  // Modals visibility states
  const [isKYCModalOpen, setIsKYCModalOpen] = useState(false);
  const [isAddEquipmentOpen, setIsAddEquipmentOpen] = useState(false);
  const [accountRefreshKey, setAccountRefreshKey] = useState(0);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  
  // Contract Viewer Modal
  const [viewingContractBookingId, setViewingContractBookingId] = useState(null);
  const [viewingContractData, setViewingContractData] = useState(null);

  // Inspection Modal
  const [inspectionModalData, setInspectionModalData] = useState(null);
  const [inspectionType, setInspectionType] = useState('check_in');

  // The catalogue is authoritative from FastAPI; failures are shown to the user.
  const changeCatalogueFilters = useCallback((changes) => {
    setCatalogueFilters((current) => ({ ...current, ...changes }));
  }, []);

  const resetCatalogueFilters = useCallback(() => {
    setCatalogueFilters({
      search: '', category: 'all', city: 'Toutes les villes', prix_min: null,
      prix_max: null, verified: false, available: true, radius: 25, position: null,
    });
  }, []);

  const loadCatalogue = useCallback(async ({ append = false, offset = 0, signal } = {}) => {
    const requestNumber = append ? catalogueRequestRef.current : catalogueRequestRef.current + 1;
    if (!append) catalogueRequestRef.current = requestNumber;
    if (append) setCatalogueLoadingMore(true);
    else setCatalogueLoading(true);
    setCatalogueError(null);
    try {
      const page = await getEquipmentPage({
        ...catalogueFilters,
        lat: catalogueFilters.position?.lat,
        lng: catalogueFilters.position?.lng,
        radius_km: catalogueFilters.radius,
        limit: PAGE_SIZE,
        offset,
      }, { signal });
      const mapped = page.items.map(item => ({
        ...item,
        rating: item.rating ?? null,
        reviews_count: item.reviews_count ?? null,
        image: item.photos?.[0] || item.images_urls?.[0] || null,
        is_verified: item.loueur_statut_kyc === 'verified' || item.is_verified === true,
        specs: item.specs_json || item.specs || {}
      }));
      if (!append && requestNumber !== catalogueRequestRef.current) return;
      setEquipmentList((current) => append
        ? [...new Map([...current, ...mapped].map((item) => [item.id, item])).values()]
        : mapped);
      const loadedCount = offset + mapped.length;
      setCatalogueTotal(page.total);
      setCatalogueHasMore(page.total != null ? loadedCount < page.total : mapped.length === PAGE_SIZE);
      setHomepageCities((current) => [...new Set([...current, ...mapped.map((item) => item.city).filter(Boolean)])]
        .sort((left, right) => left.localeCompare(right, 'fr')));
    } catch (error) {
      if (error.name === 'AbortError' || error.code === 'REQUEST_CANCELLED') return;
      if (!append && requestNumber !== catalogueRequestRef.current) return;
      if (!append) setEquipmentList([]);
      setCatalogueError(catalogueErrorMessage(error));
    } finally {
      if (append) setCatalogueLoadingMore(false);
      else if (requestNumber === catalogueRequestRef.current) setCatalogueLoading(false);
    }
  }, [catalogueFilters]);

  useEffect(() => {
    const controller = new AbortController();
    loadCatalogue({ signal: controller.signal });
    return () => controller.abort();
  }, [catalogueFilters, loadCatalogue]);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await getEquipmentCategories();
        const rows = response?.donnees ?? response ?? [];
        setHomepageCategories(rows.map((item) => ({
          id: item.categorie ?? item.category ?? item.id,
          label: item.nom_affiche || categoryLabel(item.categorie ?? item.category ?? item.id),
        })).filter((item) => item.id));
      } catch {
        // The catalogue remains usable; category discovery is an optional facet.
      }
    };
    loadCategories();
  }, []);

  useEffect(() => {
    const params = new URLSearchParams();
    if (catalogueFilters.search) params.set('q', catalogueFilters.search);
    if (catalogueFilters.category !== 'all') params.set('category', catalogueFilters.category);
    if (catalogueFilters.city !== 'Toutes les villes') params.set('city', catalogueFilters.city);
    if (catalogueFilters.prix_min != null) params.set('min_price', catalogueFilters.prix_min);
    if (catalogueFilters.prix_max != null) params.set('max_price', catalogueFilters.prix_max);
    if (catalogueFilters.verified) params.set('verified', 'true');
    if (!catalogueFilters.available) params.set('available', 'false');
    if (catalogueFilters.position) params.set('radius', catalogueFilters.radius);
    const query = params.toString();
    window.history.replaceState(null, '', `${window.location.pathname}${query ? `?${query}` : ''}${window.location.hash}`);
  }, [catalogueFilters]);

  const handleSelectEquipment = (item, mode) => {
    setSelectedEquipment(item);
    setEquipmentModalMode(mode);
  };

  const handleEquipmentAdded = () => {
    loadCatalogue();
    setAccountRefreshKey((current) => current + 1);
  };

  const navigate = (view) => {
    setCurrentView(view);
    if (view === 'dashboard') {
      if (!window.location.hash.startsWith('#account-')) {
        window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}#account-overview`);
      }
    } else if (window.location.hash.startsWith('#account-')) {
      window.history.replaceState(null, '', `${window.location.pathname}${window.location.search}`);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleRentOut = () => {
    if (currentUser) setIsAddEquipmentOpen(true);
    else setIsAuthModalOpen(true);
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
      setCurrentUser(user);
      setIsKYCVerified(user?.statut_verification === 'verified');
      setSessionError(null);
    }, (error) => setSessionError(`Session API indisponible : ${error.message}`));
    return () => {
      if (typeof unsubscribe === 'function') unsubscribe();
    };
  }, []);

  const handleLogout = async () => {
    setSessionError(null);
    try {
      await logoutUser();
      setCurrentUser(null);
    } catch (error) {
      setSessionError(`Déconnexion API incomplète : ${error.message}`);
    }
  };

  const handleKYCStatusChange = useCallback((status) => {
    setCurrentUser((user) => {
      if (!user || user.statut_verification === status) return user;
      return { ...user, statut_verification: status };
    });
    setIsKYCVerified(status === 'verified');
  }, []);

  // Dynamic SEO & GEO Page Metadata
  useEffect(() => {
    let title = "Lokiini — Location de matériel au Maroc";
    if (catalogueFilters.city && catalogueFilters.city !== 'Toutes les villes') {
      title = `Location de Matériel & Équipements à ${catalogueFilters.city} — Lokiini Maroc`;
    }
    if (catalogueFilters.category && catalogueFilters.category !== 'all') {
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
      title = `Location ${catNames[catalogueFilters.category] || categoryLabel(catalogueFilters.category)} au Maroc — Lokiini`;
    }
    document.title = title;
  }, [catalogueFilters.city, catalogueFilters.category]);

  return (
    <div className="flex min-h-screen flex-col bg-lokiini-sand pb-[calc(5.5rem+env(safe-area-inset-bottom))] lg:pb-0">
      
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
      <main id="main-content" tabIndex="-1" className="flex-1 focus:outline-none">
        {sessionError && (
          <Container size="lg" className="pt-4"><div role="alert" className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-semibold text-red-800">{sessionError}</div></Container>
        )}
        {currentView === 'catalog' ? (
          <>
            {/* Hero & Search Bar */}
            <Hero
              selectedCity={catalogueFilters.city}
              setSelectedCity={(city) => changeCatalogueFilters({ city })}
              searchTerm={catalogueFilters.search}
              setSearchTerm={(search) => changeCatalogueFilters({ search })}
              onRentOut={handleRentOut}
            />

            <CatalogueExperience
              equipmentList={equipmentList}
              total={catalogueTotal}
              categories={homepageCategories}
              filters={catalogueFilters}
              onChangeFilters={changeCatalogueFilters}
              onResetFilters={resetCatalogueFilters}
              onSelectEquipment={handleSelectEquipment}
              loading={catalogueLoading}
              loadingMore={catalogueLoadingMore}
              hasMore={catalogueHasMore}
              error={catalogueError}
              onRetry={() => loadCatalogue()}
              onLoadMore={() => loadCatalogue({ append: true, offset: equipmentList.length })}
            />

            <GeoCitiesSection
              cities={homepageCities}
              selectedCity={catalogueFilters.city}
              onSelectCity={(city) => {
                changeCatalogueFilters({ city });
                requestAnimationFrame(() => document.getElementById('catalogue-grid')?.scrollIntoView({ behavior: 'smooth' }));
              }}
            />

            <HowLokiiniWorks />
            <TrustSafetySection />
            <OwnerCallToAction onRentOut={handleRentOut} />
            <FAQSection />
          </>
        ) : currentView === 'pricing' ? (
          /* Dedicated Pricing View */
          <PageShell className="bg-stone-50">
            <Container className="mb-2">
              <Breadcrumb items={[{
                label: t('nav.browseShort'),
                href: '#catalogue',
                onClick: (event) => { event.preventDefault(); navigate('catalog'); },
              }, { label: t('nav.pricing') }]} />
            </Container>
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
          </PageShell>
        ) : currentUser ? (
          /* One account for renting and owning */
          <AccountDashboard
            onNewEquipment={() => setIsAddEquipmentOpen(true)}
            onOpenContract={handleOpenContract}
            onOpenInspection={handleOpenInspection}
            onOpenKYC={() => setIsKYCModalOpen(true)}
            onNavigate={navigate}
            currentUser={currentUser}
            refreshKey={accountRefreshKey}
            onUserUpdated={(user) => {
              setCurrentUser(user);
              setIsKYCVerified(user?.statut_verification === 'verified');
            }}
          />
        ) : (
          /* Non-authenticated Dashboard Gate */
          <PageShell className="bg-stone-50">
            <Container size="md">
              <Breadcrumb items={[{
                label: t('nav.browseShort'),
                href: '#catalogue',
                onClick: (event) => { event.preventDefault(); navigate('catalog'); },
              }, { label: t('nav.dashboard') }]} className="mb-8" />
              <Card className="mx-auto max-w-lg space-y-5 p-7 text-center sm:p-8">
              <div className="w-16 h-16 bg-emerald-50 text-lokiini-teal rounded-2xl flex items-center justify-center mx-auto shadow-inner">
                <Lock className="w-8 h-8" />
              </div>
              <h1 className="font-display text-2xl font-bold text-ink">
                {t('dashboard.gateTitle')}
              </h1>
              <p className="text-sm leading-6 text-muted">
                {t('dashboard.gateDescription')}
              </p>
              <div className="flex flex-col sm:flex-row gap-3 pt-2">
                <Button
                  onClick={() => setIsAuthModalOpen(true)}
                  className="flex-1"
                >
                  {t('footer.signIn')}
                </Button>
                <Button
                  variant="secondary"
                  onClick={() => navigate('catalog')}
                  className="flex-1"
                >
                  {t('nav.browse')}
                </Button>
              </div>
              </Card>
            </Container>
          </PageShell>
        )}
      </main>

      <Footer
        currentUser={currentUser}
        onNavigate={navigate}
        onRentOut={handleRentOut}
        onOpenAuth={() => setIsAuthModalOpen(true)}
      />

      {/* 4. Equipment Details & Booking Modal */}
      {selectedEquipment && (
        <EquipmentModal
          equipment={selectedEquipment}
          initialMode={equipmentModalMode}
          isAuthenticated={Boolean(currentUser)}
          isKYCVerified={isKYCVerified}
          onOpenKYC={() => setIsKYCModalOpen(true)}
          onOpenAuth={() => setIsAuthModalOpen(true)}
          onClose={() => setSelectedEquipment(null)}
          onBookingSuccess={() => loadCatalogue()}
          onOpenContract={handleOpenContract}
          onOpenInspection={handleOpenInspection}
          onSelectSimilar={(item) => setSelectedEquipment(item)}
        />
      )}

      {/* 5. KYC Verification Modal */}
      <KYCVerificationModal
        isOpen={isKYCModalOpen}
        onClose={() => setIsKYCModalOpen(false)}
        currentUser={currentUser}
        onStatusChange={handleKYCStatusChange}
      />

      {/* 6. Add Equipment Modal (Pro Owner) */}
      <AddEquipmentModal
        isOpen={isAddEquipmentOpen}
        onClose={() => setIsAddEquipmentOpen(false)}
        onEquipmentAdded={handleEquipmentAdded}
      />

      {/* 7. Check-in / check-out inspection */}
      {inspectionModalData && (
        <InspectionModal
          isOpen={!!inspectionModalData}
          onClose={() => setInspectionModalData(null)}
          booking={inspectionModalData}
          type={inspectionType}
          currentUser={currentUser}
          onInspectionSuccess={() => {
            setAccountRefreshKey((value) => value + 1);
            loadCatalogue();
          }}
        />
      )}

      {/* 8. DOC Lease Contract Viewer Modal */}
      {viewingContractBookingId && (
        <ContractViewerModal
          isOpen={!!viewingContractBookingId}
          onClose={() => setViewingContractBookingId(null)}
          bookingId={viewingContractBookingId}
          bookingData={viewingContractData}
          onContractUpdated={() => setAccountRefreshKey((value) => value + 1)}
        />
      )}

      {/* 9. Auth Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={(user) => {
          setCurrentUser(user);
          setIsKYCVerified(user?.statut_verification === 'verified');
        }}
      />

    </div>
  );
}
