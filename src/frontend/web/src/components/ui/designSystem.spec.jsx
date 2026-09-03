import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it, vi } from 'vitest';

import { I18nProvider } from '../../i18n';
import { ErrorState, Input, Modal, Tabs } from './index';

function withLocale(component) {
  return render(<I18nProvider>{component}</I18nProvider>);
}

describe('critical shared components', () => {
  it('links form errors to the input for assistive technology', () => {
    withLocale(<Input label="Date de début" error="Date indisponible" />);
    const input = screen.getByLabelText('Date de début');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAccessibleDescription('Date indisponible');
    expect(screen.getByRole('alert')).toHaveTextContent('Date indisponible');
  });

  it('changes tabs by keyboard and exposes the matching panel', async () => {
    const user = userEvent.setup();
    withLocale(<Tabs items={[
      { value: 'bookings', label: 'Réservations', content: 'Liste des réservations' },
      { value: 'payments', label: 'Paiements', content: 'Suivi des paiements' },
    ]} />);
    const bookings = screen.getByRole('tab', { name: 'Réservations' });
    bookings.focus();
    await user.keyboard('{ArrowRight}');
    expect(screen.getByRole('tab', { name: 'Paiements' })).toHaveAttribute('aria-selected', 'true');
    expect(screen.getByRole('tabpanel')).toHaveTextContent('Suivi des paiements');
  });

  it('closes dialogs with Escape and provides a recoverable error action', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    const onRetry = vi.fn();
    withLocale(<>
      <Modal open onClose={onClose} title="Confirmation">Contenu protégé</Modal>
      <ErrorState title="API indisponible" onRetry={onRetry} />
    </>);
    await user.keyboard('{Escape}');
    expect(onClose).toHaveBeenCalledTimes(1);
    await user.click(screen.getByRole('button', { name: 'Réessayer' }));
    expect(onRetry).toHaveBeenCalledTimes(1);
  });
});

