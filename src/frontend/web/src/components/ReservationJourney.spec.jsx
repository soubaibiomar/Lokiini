import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({
  calculatePricing: vi.fn(),
  createBooking: vi.fn(),
}));

vi.mock('../services/api', () => api);

import ReservationJourney from './ReservationJourney';
import { I18nProvider } from '../i18n';

const equipment = {
  id: 'equipment-1',
  titre: 'Perceuse test',
  montant_caution: 300,
  niveau_risque: 'faible',
  kyc_requis: false,
};
const pricing = {
  nombre_jours: 3,
  total_location_mad: 300,
  frais_service_plateforme_mad: 45,
  montant_caution_mad: 300,
  total_a_payer_a_la_remise_mad: 645,
};

function renderJourney(props = {}) {
  return render(
    <I18nProvider>
      <ReservationJourney
        equipment={equipment}
        ownerName="Owner Test"
        isAuthenticated
        isKYCVerified
        onOpenKYC={vi.fn()}
        onOpenAuth={vi.fn()}
        onBookingSuccess={vi.fn()}
        onClose={vi.fn()}
        {...props}
      />
    </I18nProvider>,
  );
}

async function reachReview(user) {
  await waitFor(() => expect(api.calculatePricing).toHaveBeenCalledTimes(1));
  const continueButton = () => screen.getByRole('button', { name: 'Continuer' });
  await user.click(continueButton());
  await user.click(continueButton());
  await user.click(continueButton());
  await user.click(screen.getByRole('checkbox'));
}

describe('reservation form behavior', () => {
  beforeEach(() => {
    api.calculatePricing.mockResolvedValue(pricing);
    api.createBooking.mockReset();
  });

  it('uses the server quote and returns date conflicts to editable dates', async () => {
    api.createBooking.mockRejectedValue({ code: 'BOOKING_DATE_UNAVAILABLE' });
    const user = userEvent.setup();
    renderJourney();
    await reachReview(user);

    expect(screen.getByLabelText('Récapitulatif permanent de la réservation')).toHaveTextContent(/300.*MAD/);
    await user.click(screen.getByRole('button', { name: /Envoyer la demande/i }));

    expect(await screen.findByRole('heading', { name: 'Choisissez vos dates' })).toBeInTheDocument();
    expect(screen.getByRole('alert')).toHaveTextContent('Ces dates ne sont plus disponibles');
    expect(api.createBooking).toHaveBeenCalledWith(
      equipment.id,
      expect.any(String),
      expect.any(String),
    );
  });

  it('blocks duplicate submissions while the first request is pending', async () => {
    let resolveBooking;
    api.createBooking.mockImplementation(() => new Promise((resolve) => { resolveBooking = resolve; }));
    const user = userEvent.setup();
    renderJourney();
    await reachReview(user);

    const submit = screen.getByRole('button', { name: /Envoyer la demande/i });
    await user.dblClick(submit);
    expect(api.createBooking).toHaveBeenCalledTimes(1);
    expect(submit).toBeDisabled();

    resolveBooking({ reservation_id: 'booking-12345678' });
    expect(await screen.findByText('Demande envoyée')).toBeInTheDocument();
  });
});
