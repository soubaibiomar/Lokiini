import React from 'react';
import { act, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const authState = vi.hoisted(() => ({ onUser: null, onError: null }));

vi.mock('./services/firebase', () => ({
  subscribeToAuthState: vi.fn((onUser, onError) => {
    authState.onUser = onUser;
    authState.onError = onError;
    return vi.fn();
  }),
  logoutUser: vi.fn(),
}));

vi.mock('./services/api', () => ({
  getEquipmentPage: vi.fn().mockResolvedValue({ items: [], total: 0 }),
  getEquipmentCategories: vi.fn().mockResolvedValue([]),
}));

vi.mock('./i18n', () => ({
  useI18n: () => ({ t: (key) => key }),
}));

vi.mock('./components/Navbar', () => ({
  default: ({ setCurrentView, currentUser }) => (
    <nav>
      <button type="button" onClick={() => setCurrentView('dashboard')}>dashboard-nav</button>
      <span>{currentUser ? 'signed-in-nav' : 'anonymous-nav'}</span>
    </nav>
  ),
}));
vi.mock('./components/Hero', () => ({ default: () => <div>hero</div> }));
vi.mock('./components/CatalogueExperience', () => ({ default: () => <div>catalogue</div> }));
vi.mock('./components/GeoCitiesSection', () => ({ default: () => null }));
vi.mock('./components/FAQSection', () => ({ default: () => null }));
vi.mock('./components/PricingSection', () => ({ default: () => null }));
vi.mock('./components/HomeSections', () => ({
  HowLokiiniWorks: () => null,
  OwnerCallToAction: () => null,
  TrustSafetySection: () => null,
}));
vi.mock('./components/EquipmentModal', () => ({ default: () => null }));
vi.mock('./components/KYCVerificationModal', () => ({ default: () => null }));
vi.mock('./components/AddEquipmentModal', () => ({ default: () => null }));
vi.mock('./components/InspectionModal', () => ({ default: () => null }));
vi.mock('./components/ContractViewerModal', () => ({ default: () => null }));
vi.mock('./components/AuthModal', () => ({ default: () => null }));
vi.mock('./components/AccountDashboard', () => ({
  default: ({ currentUser }) => <section>account:{currentUser.nom_complet}</section>,
}));
vi.mock('./components/layout', () => ({
  Footer: () => null,
  Container: ({ children }) => <div>{children}</div>,
  PageShell: ({ children }) => <div>{children}</div>,
}));
vi.mock('./components/ui', () => ({
  Breadcrumb: () => null,
  Button: ({ children, ...props }) => <button type="button" {...props}>{children}</button>,
  Card: ({ children }) => <div>{children}</div>,
}));

import App from './App';

describe('application authentication boundary', () => {
  beforeEach(() => {
    authState.onUser = null;
    authState.onError = null;
  });

  it('keeps an anonymous user behind the account gate and restores a server session', async () => {
    const user = userEvent.setup();
    render(<App />);

    await user.click(screen.getByRole('button', { name: 'dashboard-nav' }));
    expect(screen.getByRole('heading', { name: 'dashboard.gateTitle' })).toBeInTheDocument();
    expect(screen.queryByText(/^account:/)).not.toBeInTheDocument();

    act(() => authState.onUser({ id: 'user-1', nom_complet: 'Amina Test', statut_verification: 'verified' }));
    expect(screen.getByText('account:Amina Test')).toBeInTheDocument();
    expect(screen.getByText('signed-in-nav')).toBeInTheDocument();
  });

  it('shows restoration failures instead of silently assuming an authenticated user', () => {
    render(<App />);
    act(() => authState.onError(new Error('FastAPI unreachable')));
    expect(screen.getByRole('alert')).toHaveTextContent('Session API indisponible : FastAPI unreachable');
    expect(screen.getByText('anonymous-nav')).toBeInTheDocument();
  });
});

