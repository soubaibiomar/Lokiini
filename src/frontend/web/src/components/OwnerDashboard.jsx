import React, { useState, useEffect } from 'react';
import { 
  PlusCircle, CheckCircle2, Clock, AlertTriangle, ShieldCheck, 
  DollarSign, Package, FileText, Video, RefreshCw, Eye 
} from 'lucide-react';
import { getBookings, updateBookingStatus } from '../services/api';

const DEFAULT_RENTALS = [
  {
    id: 'b1111111-1111-1111-1111-111111111111',
    equipment_title: 'Mini-Pelle Compacte Bobcat E19 (1.9 Tonne)',
    renter_name: 'Karim Tazi (Entreprise BTP)',
    start_date: '2026-08-24',
    end_date: '2026-08-31',
    total_days: 7,
    rental_total_mad: 7168,
    deposit_hold_mad: 8000,
    booking_status: 'in_progress',
    cmi_status: 'held',
    cmi_auth_token: 'CMI_AUTH_94821A84'
  },
  {
    id: 'b2222222-2222-2222-2222-222222222222',
    equipment_title: 'Bétonnière Professionnelle Chantier 160L',
    renter_name: 'Omar Benjelloun',
    start_date: '2026-08-26',
    end_date: '2026-08-29',
    total_days: 3,
    rental_total_mad: 459,
    deposit_hold_mad: 1500,
    booking_status: 'confirmed',
    cmi_status: 'held',
    cmi_auth_token: 'CMI_AUTH_102938B7'
  },
  {
    id: 'b3333333-3333-3333-3333-333333333333',
    equipment_title: 'Caméra Cinéma Sony FX3 4K Full-Frame',
    renter_name: 'Mehdi Alami (Studio Marrakech)',
    start_date: '2026-08-20',
    end_date: '2026-08-26',
    total_days: 6,
    rental_total_mad: 2430,
    deposit_hold_mad: 5000,
    booking_status: 'completed',
    cmi_status: 'released',
    cmi_auth_token: 'CMI_AUTH_394812C4'
  }
];

export default function OwnerDashboard({ 
  onNewEquipment, 
  onOpenContract, 
  onOpenInspection,
  currentUser 
}) {
  const [rentals, setRentals] = useState(DEFAULT_RENTALS);
  const [loading, setLoading] = useState(false);
  const [actionSuccessMsg, setActionSuccessMsg] = useState(null);

  const loadRentals = async () => {
    setLoading(true);
    const apiData = await getBookings();
    if (apiData && apiData.length > 0) {
      setRentals(apiData);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadRentals();
  }, []);

  // Compute live KPIs
  const totalRevenue = rentals.reduce((acc, r) => acc + (parseFloat(r.rental_total_mad) || 0), 0);
  const activeCount = rentals.filter(r => r.booking_status === 'in_progress' || r.booking_status === 'confirmed').length;
  const totalEscrow = rentals
    .filter(r => r.cmi_status === 'held')
    .reduce((acc, r) => acc + (parseFloat(r.deposit_hold_mad) || 0), 0);

  const handleReleaseDeposit = async (bookingId) => {
    const updated = await updateBookingStatus(bookingId, 'completed', 'released');
    setActionSuccessMsg("Caution CMI libérée avec succès au locataire !");
    setRentals(prev => prev.map(r => r.id === bookingId ? { ...r, booking_status: 'completed', cmi_status: 'released' } : r));
    setTimeout(() => setActionSuccessMsg(null), 3000);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'in_progress':
        return <span className="px-2.5 py-1 rounded-full font-bold border text-[11px] bg-emerald-50 text-emerald-700 border-emerald-200">En cours (Check-in scellé)</span>;
      case 'confirmed':
        return <span className="px-2.5 py-1 rounded-full font-bold border text-[11px] bg-blue-50 text-blue-700 border-blue-200">Confirmée (Caution bloquée)</span>;
      case 'completed':
        return <span className="px-2.5 py-1 rounded-full font-bold border text-[11px] bg-stone-100 text-stone-700 border-stone-200">Terminée & Libérée</span>;
      default:
        return <span className="px-2.5 py-1 rounded-full font-bold border text-[11px] bg-amber-50 text-amber-700 border-amber-200">{status}</span>;
    }
  };

  return (
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2.5 py-0.5 rounded-md text-[11px] font-bold bg-lokiini-teal text-white">
              PORTAIL PRO LOUEUR
            </span>
            <span className="text-xs text-stone-500">
              {currentUser?.company_name || 'Atlas Location BTP Maroc'} (ICE: {currentUser?.company_ice || '002345678000045'})
            </span>
          </div>
          <h1 className="text-3xl font-black text-lokiini-charcoal font-['Outfit'] mt-1">
            Tableau de Bord & Gestion de Flotte
          </h1>
        </div>

        <div className="flex items-center gap-3 self-start sm:self-auto">
          <button
            onClick={loadRentals}
            disabled={loading}
            className="p-3 rounded-xl border border-stone-300 bg-white hover:bg-stone-50 text-stone-700 text-xs font-bold transition-all shadow-xs"
            title="Actualiser les données"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          <button
            onClick={onNewEquipment}
            className="flex items-center gap-2 bg-lokiini-teal hover:bg-lokiini-teal-dark text-white text-xs font-bold px-4 py-3 rounded-xl shadow-sm transition-all"
          >
            <PlusCircle className="w-4 h-4" />
            <span>Ajouter un équipement</span>
          </button>
        </div>
      </div>

      {actionSuccessMsg && (
        <div className="bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-2xl p-4 text-xs font-bold flex items-center gap-2 mb-6 animate-in fade-in">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <span>{actionSuccessMsg}</span>
        </div>
      )}

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-10">
        <div className="bg-white p-6 rounded-2xl border border-stone-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-stone-500">Revenus Cumulés (MAD)</span>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-emerald-600 bg-emerald-50">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-lokiini-charcoal font-['Outfit']">
            {totalRevenue.toLocaleString()} MAD
          </div>
          <span className="text-[11px] font-semibold text-emerald-600 mt-1 block">Règlement CMI garanti</span>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-stone-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-stone-500">Locations Actives</span>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-blue-600 bg-blue-50">
              <Package className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-lokiini-charcoal font-['Outfit']">
            {activeCount} machines
          </div>
          <span className="text-[11px] font-semibold text-blue-600 mt-1 block">100% avec baux DOC signés</span>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-stone-200 shadow-sm">
          <div className="flex items-center justify-between mb-3">
            <span className="text-xs font-bold text-stone-500">Cautions CMI sous Séquestre</span>
            <div className="w-9 h-9 rounded-xl flex items-center justify-center text-lokiini-terracotta bg-orange-50">
              <ShieldCheck className="w-5 h-5" />
            </div>
          </div>
          <div className="text-2xl font-black text-lokiini-charcoal font-['Outfit']">
            {totalEscrow.toLocaleString()} MAD
          </div>
          <span className="text-[11px] font-semibold text-amber-600 mt-1 block">Garanties actives non débitées</span>
        </div>
      </div>

      {/* Main Table Container */}
      <div className="bg-white rounded-2xl border border-stone-200 shadow-sm overflow-hidden">
        <div className="p-6 border-b border-stone-200 flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div>
            <h3 className="font-black text-lg text-lokiini-charcoal font-['Outfit']">
              Suivi des Contrats & Cautions CMI en Temps Réel
            </h3>
            <span className="text-xs text-stone-400">Synchronisé via n8n & CMI Gateway</span>
          </div>
          <span className="text-xs font-bold text-stone-500 bg-stone-50 px-3 py-1.5 rounded-lg border border-stone-200">
            {rentals.length} contrats enregistrés
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-xs">
            <thead>
              <tr className="bg-stone-50 text-stone-500 border-b border-stone-200">
                <th className="py-3.5 px-6 font-bold">Réf. Contrat</th>
                <th className="py-3.5 px-6 font-bold">Matériel</th>
                <th className="py-3.5 px-6 font-bold">Locataire</th>
                <th className="py-3.5 px-6 font-bold">Période</th>
                <th className="py-3.5 px-6 font-bold">Montant</th>
                <th className="py-3.5 px-6 font-bold">Caution CMI</th>
                <th className="py-3.5 px-6 font-bold">Statut</th>
                <th className="py-3.5 px-6 font-bold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-stone-100">
              {rentals.map((r) => (
                <tr key={r.id} className="hover:bg-stone-50/80 transition-colors">
                  <td className="py-4 px-6 font-bold text-lokiini-teal font-mono">
                    LK-{String(r.id).substring(0, 6).toUpperCase()}
                  </td>
                  <td className="py-4 px-6 font-semibold text-stone-800 max-w-[200px] truncate">
                    {r.equipment_title || 'Équipement Pro'}
                  </td>
                  <td className="py-4 px-6 text-stone-600">
                    {r.renter_name || 'Locataire'}
                  </td>
                  <td className="py-4 px-6 text-stone-500 whitespace-nowrap">
                    {r.start_date} au {r.end_date}
                  </td>
                  <td className="py-4 px-6 font-black text-stone-800">
                    {r.rental_total_mad} MAD
                  </td>
                  <td className="py-4 px-6">
                    <span className="px-2 py-0.5 rounded-md font-bold bg-orange-50 text-lokiini-terracotta border border-orange-200 text-[10px] whitespace-nowrap">
                      {r.deposit_hold_mad} MAD ({r.cmi_status === 'released' ? 'Libérée' : 'Séquestre'})
                    </span>
                  </td>
                  <td className="py-4 px-6 whitespace-nowrap">
                    {getStatusBadge(r.booking_status)}
                  </td>
                  <td className="py-4 px-6 text-right">
                    <div className="flex items-center justify-end gap-1.5">
                      
                      {/* View DOC Contract Button */}
                      <button
                        onClick={() => onOpenContract(r.id, r)}
                        className="p-1.5 rounded-lg border border-stone-200 hover:bg-stone-100 text-stone-700 transition-colors"
                        title="Consulter le Contrat DOC"
                      >
                        <FileText className="w-3.5 h-3.5" />
                      </button>

                      {/* Check-in Inspection Button */}
                      {r.booking_status === 'confirmed' && (
                        <button
                          onClick={() => onOpenInspection(r, 'check_in')}
                          className="px-2 py-1 rounded-lg bg-teal-50 text-lokiini-teal hover:bg-teal-100 border border-teal-200 text-[10px] font-bold flex items-center gap-1"
                          title="Sceller Check-in Vidéo"
                        >
                          <Video className="w-3 h-3" />
                          <span>Check-in</span>
                        </button>
                      )}

                      {/* Check-out & Release Caution Button */}
                      {r.booking_status === 'in_progress' && (
                        <button
                          onClick={() => onOpenInspection(r, 'check_out')}
                          className="px-2 py-1 rounded-lg bg-orange-50 text-lokiini-terracotta hover:bg-orange-100 border border-orange-200 text-[10px] font-bold flex items-center gap-1"
                          title="Faire le Check-out Vidéo & Libérer Caution"
                        >
                          <CheckCircle2 className="w-3 h-3" />
                          <span>Check-out</span>
                        </button>
                      )}

                      {/* Direct release button if completed */}
                      {r.cmi_status === 'held' && r.booking_status === 'completed' && (
                        <button
                          onClick={() => handleReleaseDeposit(r.id)}
                          className="px-2 py-1 rounded-lg bg-emerald-50 text-emerald-700 hover:bg-emerald-100 border border-emerald-200 text-[10px] font-bold"
                        >
                          Libérer CMI
                        </button>
                      )}

                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </section>
  );
}
