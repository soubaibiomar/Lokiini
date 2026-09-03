import React from 'react';
import {
  Bell, CalendarDays, CircleDollarSign, FileText, LayoutDashboard, MessageSquare,
  Package, PlusCircle, RefreshCw, Scale, Settings, ShieldCheck, Star, WalletCards,
} from 'lucide-react';
import { Avatar, Badge, Breadcrumb, Button, cn } from '../ui';
import { Container, PageShell } from './Container';
import { useI18n } from '../../i18n';

const SECTION_ICONS = {
  overview: LayoutDashboard,
  bookings: CalendarDays,
  equipment: Package,
  messages: MessageSquare,
  disputes: Scale,
  payments: WalletCards,
  earnings: CircleDollarSign,
  documents: FileText,
  verification: ShieldCheck,
  reviews: Star,
  notifications: Bell,
  settings: Settings,
};

export default function DashboardShell({
  currentUser, onNavigate, onNewEquipment, onRefresh, refreshing,
  sections, activeSection, onSectionChange, sectionCounts = {}, children,
}) {
  const { t } = useI18n();
  const displayName = currentUser?.company_name || currentUser?.nom_complet || currentUser?.full_name || currentUser?.email || 'Lokiini';
  const localizedSections = sections.map((section) => ({ ...section, label: t(`dashboard.sections.${section.id}`, {}, section.label) }));
  const activeLabel = localizedSections.find((section) => section.id === activeSection)?.label || t('dashboard.account');

  return (
    <PageShell>
      <Container>
        <Breadcrumb items={[{
          label: t('nav.browseShort'),
          href: '#catalogue',
          onClick: (event) => {
            event.preventDefault();
            onNavigate?.('catalog');
          },
        }, { label: t('dashboard.account') }]} className="mb-5" />

        <div className="mb-5 rounded-card border border-border bg-surface p-4 shadow-subtle lg:hidden">
          <div className="flex items-center gap-3">
            <Avatar src={currentUser?.avatar_url || currentUser?.photoURL} name={displayName} />
            <div className="min-w-0">
              <p className="truncate text-sm font-bold text-ink">{displayName}</p>
              <p className="truncate text-xs text-muted">{t('dashboard.singleAccount')}</p>
            </div>
          </div>
          <label className="mt-4 block">
            <span className="ui-label">{t('dashboard.accountNav')}</span>
            <select
              className="ui-control"
              value={activeSection}
              onChange={(event) => onSectionChange(event.target.value)}
            >
              {localizedSections.map((section) => {
                const count = Number(sectionCounts[section.id]) || 0;
                return <option key={section.id} value={section.id}>{section.label}{count > 0 ? ` (${count})` : ''}</option>;
              })}
            </select>
          </label>
          <Button variant="action" className="mt-3 w-full" onClick={onNewEquipment}>
            <PlusCircle aria-hidden="true" className="size-4" /> {t('dashboard.publish')}
          </Button>
        </div>

        <div className="grid gap-6 lg:grid-cols-[236px_minmax(0,1fr)] lg:gap-8">
          <aside className="hidden min-w-0 lg:sticky lg:top-24 lg:block lg:h-[calc(100vh-7rem)]">
            <div className="rounded-card border border-border bg-surface p-3 shadow-subtle lg:flex lg:h-full lg:flex-col">
              <div className="flex items-center gap-3 border-b border-border px-1 pb-4 pt-1">
                <Avatar src={currentUser?.avatar_url || currentUser?.photoURL} name={displayName} />
                <div className="min-w-0">
                  <p className="truncate text-sm font-bold text-ink">{displayName}</p>
                  <p className="truncate text-xs text-muted">{t('dashboard.singleAccount')}</p>
                </div>
              </div>

              <nav aria-label={t('dashboard.accountNav')} className="-mx-1 mt-3 space-y-1 overflow-y-auto overflow-x-hidden px-1 pb-1">
                {localizedSections.map((section) => {
                  const Icon = SECTION_ICONS[section.id] || LayoutDashboard;
                  const selected = activeSection === section.id;
                  const count = sectionCounts[section.id];
                  return (
                    <button
                      key={section.id}
                      type="button"
                      aria-current={selected ? 'page' : undefined}
                      onClick={() => onSectionChange(section.id)}
                      className={cn(
                        'flex min-h-10 w-full items-center gap-2 rounded-lg px-3 text-start text-xs font-bold transition-colors',
                        selected ? 'bg-primary-subtle text-primary' : 'text-muted hover:bg-stone-100 hover:text-ink',
                      )}
                    >
                      <Icon aria-hidden="true" className="size-4 shrink-0" />
                      <span>{section.label}</span>
                      {Number(count) > 0 && <Badge variant={selected ? 'primary' : 'neutral'} className="ms-auto">{count}</Badge>}
                    </button>
                  );
                })}
              </nav>

              <Button variant="action" size="sm" className="mt-3 w-full lg:mt-auto" onClick={onNewEquipment}>
                <PlusCircle aria-hidden="true" className="size-4" /> {t('dashboard.publish')}
              </Button>
            </div>
          </aside>

          <div className="min-w-0">
            <header className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary">{t('dashboard.account')}</p>
                <h1 className="mt-1 font-display text-3xl font-bold tracking-tight text-ink">{activeLabel}</h1>
                <p className="mt-1 max-w-2xl text-sm leading-6 text-muted">
                  {t('dashboard.description')}
                </p>
              </div>
              <Button variant="secondary" size="sm" onClick={onRefresh} loading={refreshing} loadingLabel={t('common.refreshing')}>
                <RefreshCw aria-hidden="true" className="size-4" /> {t('common.refresh')}
              </Button>
            </header>
            {children}
          </div>
        </div>
      </Container>
    </PageShell>
  );
}
