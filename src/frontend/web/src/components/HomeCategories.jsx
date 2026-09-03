import React from 'react';
import { Camera, Hammer, Leaf, Package, Paintbrush, Sparkles, TentTree, Wrench } from 'lucide-react';
import { cn } from './ui';
import { Container } from './layout';
import { useI18n } from '../i18n';

const categoryIcons = {
  tools: Wrench,
  btp: Hammer,
  audiovisual: Camera,
  audiovisuel: Camera,
  event: Sparkles,
  evenementiel: Sparkles,
  outdoor: TentTree,
  cleaning: Sparkles,
  garden: Leaf,
  creative: Paintbrush,
};

export default function HomeCategories({ categories, selectedCategory, onSelectCategory }) {
  const { t } = useI18n();
  if (!categories.length) return null;
  return (
    <section aria-labelledby="categories-heading" className="border-b border-border bg-surface py-10 sm:py-12">
      <Container>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-primary">{t('home.categoriesEyebrow')}</p>
            <h2 id="categories-heading" className="mt-1 font-display text-2xl font-bold tracking-tight text-ink sm:text-3xl">{t('home.categoriesTitle')}</h2>
          </div>
          <button type="button" onClick={() => onSelectCategory('all')} className="self-start text-sm font-bold text-primary hover:underline sm:self-auto">{t('common.seeAll')}</button>
        </div>
        <div className="mt-6 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
          {categories.map((category) => {
            const Icon = categoryIcons[category.id] || Package;
            const active = selectedCategory === category.id;
            return (
              <button
                key={category.id}
                type="button"
                onClick={() => onSelectCategory(category.id)}
                aria-pressed={active}
                className={cn('group flex min-h-28 flex-col items-start justify-between rounded-card border p-4 text-start transition duration-180', active ? 'border-primary bg-primary-subtle shadow-subtle' : 'border-border bg-canvas hover:-translate-y-0.5 hover:border-primary/30 hover:bg-surface hover:shadow-card')}
              >
                <span className={cn('flex size-10 items-center justify-center rounded-control', active ? 'bg-primary text-white' : 'bg-surface text-primary shadow-subtle')}>
                  <Icon aria-hidden="true" className="size-5" />
                </span>
                <span className="mt-3 text-sm font-bold leading-5 text-ink">{t(`category.${category.id}`, {}, category.label)}</span>
              </button>
            );
          })}
        </div>
      </Container>
    </section>
  );
}
