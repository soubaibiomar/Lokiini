import React from 'react';
import { CircleUserRound, LayoutDashboard, LogIn, LogOut, PackageSearch, PlusCircle, ShieldCheck, UserRound } from 'lucide-react';
import { Avatar, Badge, Button, Dropdown, DropdownItem, cn } from './ui';
import { Container } from './layout';
import LanguageSwitcher from './LanguageSwitcher';
import { useI18n } from '../i18n';

export default function Navbar({
  onOpenKYC,
  onOpenAuth,
  onOpenAddEquipment,
  isKYCVerified,
  currentView,
  setCurrentView,
  currentUser,
  onLogout,
}) {
  const { t } = useI18n();
  const navigate = (view) => {
    setCurrentView(view);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };
  const rentOut = () => currentUser ? onOpenAddEquipment() : onOpenAuth();
  const displayName = currentUser?.full_name || currentUser?.email || t('dashboard.account');

  const accountTrigger = currentUser ? (
    <Button variant="secondary" className="max-w-48 px-2.5" aria-label={t('nav.openAccountMenu')}>
      <Avatar src={currentUser.avatar_url || currentUser.photoURL} name={displayName} size="sm" />
      <span className="hidden max-w-28 truncate xl:inline">{displayName.split(' ')[0]}</span>
    </Button>
  ) : null;

  return (
    <>
      <a href="#main-content" className="fixed start-4 top-3 z-[80] -translate-y-24 rounded-control bg-ink px-4 py-3 text-sm font-bold text-white shadow-raised transition-transform focus:translate-y-0">
        {t('nav.skipToContent')}
      </a>
      <header className="sticky top-0 z-40 border-b border-border bg-white/95 shadow-subtle backdrop-blur-md">
        <Container className="flex h-16 items-center justify-between gap-4 lg:h-[72px]">
          <button type="button" onClick={() => navigate('catalog')} className="flex min-h-11 shrink-0 items-center rounded-lg focus-visible:ring-2 focus-visible:ring-primary/30" aria-label={t('nav.homeAria')}>
            <img src="/logo.png" alt="Lokiini" className="h-9 w-auto object-contain sm:h-10" />
          </button>

          <nav aria-label={t('nav.primary')} className="hidden items-center gap-1 lg:flex">
            <button type="button" onClick={() => navigate('catalog')} aria-current={currentView === 'catalog' ? 'page' : undefined} className={cn('min-h-10 rounded-lg px-3 text-sm font-bold transition-colors', currentView === 'catalog' ? 'bg-primary-subtle text-primary' : 'text-muted hover:bg-stone-100 hover:text-ink')}>
              {t('nav.browse')}
            </button>
            <button type="button" onClick={() => navigate('pricing')} aria-current={currentView === 'pricing' ? 'page' : undefined} className={cn('min-h-10 rounded-lg px-3 text-sm font-bold transition-colors', currentView === 'pricing' ? 'bg-primary-subtle text-primary' : 'text-muted hover:bg-stone-100 hover:text-ink')}>
              {t('nav.pricing')}
            </button>
            {currentUser && (
              <button type="button" onClick={() => navigate('dashboard')} aria-current={currentView === 'dashboard' ? 'page' : undefined} className={cn('min-h-10 rounded-lg px-3 text-sm font-bold transition-colors', currentView === 'dashboard' ? 'bg-primary-subtle text-primary' : 'text-muted hover:bg-stone-100 hover:text-ink')}>
                {t('nav.dashboard')}
              </button>
            )}
          </nav>

          <div className="flex items-center gap-2">
            <div className="hidden xl:block"><LanguageSwitcher compact /></div>
            <Button variant="action" className="hidden lg:inline-flex" onClick={rentOut}>
              <PlusCircle aria-hidden="true" className="size-4" /> {t('nav.rentOut')}
            </Button>

            {currentUser ? (
              <Dropdown trigger={accountTrigger} align="end" label={t('nav.accountMenu')}>
                <div className="border-b border-border px-3 py-2.5">
                  <p className="truncate text-xs font-bold text-ink">{displayName}</p>
                  <div className="mt-1">
                    <Badge variant={isKYCVerified ? 'success' : 'warning'} icon={ShieldCheck}>
                      {isKYCVerified ? t('trust.verified') : t('trust.verificationNeeded')}
                    </Badge>
                  </div>
                </div>
                <DropdownItem onClick={() => navigate('dashboard')}><LayoutDashboard aria-hidden="true" className="size-4" /> {t('nav.accountDashboard')}</DropdownItem>
                <DropdownItem onClick={() => navigate('catalog')}><PackageSearch aria-hidden="true" className="size-4" /> {t('nav.browse')}</DropdownItem>
                {!isKYCVerified && <DropdownItem onClick={onOpenKYC}><ShieldCheck aria-hidden="true" className="size-4" /> {t('nav.verifyIdentity')}</DropdownItem>}
                <DropdownItem destructive onClick={onLogout}><LogOut aria-hidden="true" className="size-4" /> {t('nav.logout')}</DropdownItem>
              </Dropdown>
            ) : (
              <Button variant="secondary" onClick={onOpenAuth}>
                <LogIn aria-hidden="true" className="size-4" /> <span className="hidden sm:inline">{t('nav.login')}</span><span className="sm:hidden">{t('common.account')}</span>
              </Button>
            )}
          </div>
        </Container>
      </header>

      <nav aria-label={t('nav.mobile')} className="fixed inset-x-0 bottom-0 z-40 border-t border-border bg-white/95 px-3 pb-[max(0.5rem,env(safe-area-inset-bottom))] pt-2 shadow-[0_-8px_24px_rgba(30,41,59,0.08)] backdrop-blur-md lg:hidden">
        <div className="mx-auto grid max-w-md grid-cols-3 gap-1">
          <button type="button" onClick={() => navigate('catalog')} aria-current={currentView === 'catalog' ? 'page' : undefined} className={cn('flex min-h-14 flex-col items-center justify-center gap-0.5 rounded-lg px-2 text-center text-[11px] font-bold leading-tight', currentView === 'catalog' ? 'bg-primary-subtle text-primary' : 'text-muted hover:bg-stone-100')}>
            <PackageSearch aria-hidden="true" className="size-5" /> {t('nav.browseShort')}
          </button>
          <button type="button" onClick={rentOut} className="flex min-h-14 flex-col items-center justify-center gap-0.5 rounded-lg bg-action px-2 text-center text-[11px] font-bold leading-tight text-white shadow-subtle hover:bg-action-hover">
            <PlusCircle aria-hidden="true" className="size-5" /> {t('nav.rentOut')}
          </button>
          <button type="button" onClick={() => currentUser ? navigate('dashboard') : onOpenAuth()} aria-current={currentView === 'dashboard' ? 'page' : undefined} className={cn('flex min-h-14 flex-col items-center justify-center gap-0.5 rounded-lg px-2 text-center text-[11px] font-bold leading-tight', currentView === 'dashboard' ? 'bg-primary-subtle text-primary' : 'text-muted hover:bg-stone-100')}>
            {currentUser ? <UserRound aria-hidden="true" className="size-5" /> : <CircleUserRound aria-hidden="true" className="size-5" />}
            {currentUser ? t('nav.dashboard') : t('nav.login')}
          </button>
        </div>
      </nav>
    </>
  );
}
