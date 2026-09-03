import { describe, expect, it } from 'vitest';

import { BOOKING_STATUS, bookingStatus } from './dashboardModel';


describe('backend-controlled booking status presentation', () => {
  it('has an explicit user-facing treatment for every lifecycle state', () => {
    const states = [
      'brouillon', 'en_attente_approbation', 'acceptee', 'paiement_en_attente',
      'confirmee', 'prete_remise', 'en_cours', 'en_attente_validation', 'termine',
      'rejete', 'annule', 'en_litige', 'resolu',
    ];
    expect(Object.keys(BOOKING_STATUS)).toEqual(states);
    for (const state of states) {
      expect(bookingStatus(state).label).not.toContain('_');
      expect(['neutral', 'warning', 'info', 'success', 'error']).toContain(bookingStatus(state).tone);
    }
  });

  it('does not promote an unknown backend value to a successful state', () => {
    expect(bookingStatus('provider_unknown')).toEqual({
      label: 'provider unknown',
      tone: 'neutral',
    });
  });
});

