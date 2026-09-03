import React from 'react';
import { PackageSearch } from 'lucide-react';
import { Button, EmptyState, EquipmentCard, ErrorState, Skeleton, cn } from './ui';
import { useI18n } from '../i18n';

export default function EquipmentGrid({ equipmentList, onSelectEquipment, hasFilters, onResetFilters, loading, loadingMore, error, onRetry, hasMore, onLoadMore, embedded = false }) {
  const { t } = useI18n();
  const sectionClass = cn(embedded ? 'min-w-0' : 'mx-auto max-w-7xl scroll-mt-24 px-4 py-12 sm:px-6 lg:px-8');
  if (loading) {
    return (
      <section className={sectionClass} aria-label={t('catalogue.loadingAria')}>
        <span className="sr-only" role="status">{t('catalogue.loading')}</span>
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
          {[0, 1, 2, 3, 4, 5].map((item) => <Skeleton key={item} className="aspect-[3/4] rounded-card" />)}
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className={sectionClass}>
        <ErrorState title={t('catalogue.loadError')} description={error} onRetry={onRetry} retryLabel={t('common.retry')} />
      </section>
    );
  }

  if (equipmentList.length === 0) {
    return (
      <section className={sectionClass}>
        <EmptyState
          icon={PackageSearch}
          title={hasFilters ? t('catalogue.noResults') : t('catalogue.empty')}
          description={hasFilters ? t('catalogue.noResultsHint') : t('catalogue.emptyHelp')}
          action={hasFilters && <Button variant="secondary" onClick={onResetFilters}>{t('catalogue.clearFilters')}</Button>}
        />
      </section>
    );
  }

  return (
    <section className={sectionClass}>
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 xl:grid-cols-3">
        {equipmentList.map((item) => (
          <EquipmentCard
            key={item.id}
            equipment={item}
            onDetails={(equipment) => onSelectEquipment(equipment, 'details')}
            onBook={(equipment) => onSelectEquipment(equipment, 'book')}
          />
        ))}
      </div>
      {hasMore && (
        <div className="mt-8 flex justify-center">
          <Button variant="secondary" size="lg" onClick={onLoadMore} loading={loadingMore} loadingLabel={t('common.loading')}>
            {t('catalogue.loadMore')}
          </Button>
        </div>
      )}
    </section>
  );
}
