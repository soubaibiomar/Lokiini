# Lokiini shared design system

This folder is the authoritative web component layer. Pages should import from `./components/ui` instead of rebuilding controls with local class strings.

## Visual language

- `primary`: deep Moroccan green for navigation, selection, trust, and secondary actions.
- `action`: terracotta for high-value actions such as search, publish, continue, and reserve.
- `canvas`: warm limestone page background.
- `surface`: calm white content surfaces.
- `ink` and `muted`: primary and secondary text.
- `success`, `warning`, `error`, and `info`: semantic state colors, each with a restrained subtle background.

Typography, spacing extensions, borders, radii, shadows, and focus styling are defined in `tailwind.config.js` and `src/index.css`. Latin text uses Plus Jakarta Sans with Outfit for display text. Noto Sans Arabic provides a compatible Arabic fallback.

## Usage

```jsx
import { Button, Input, Modal, EquipmentCard } from './components/ui';
```

Use semantic variants instead of raw brand colors. Prefer `Button variant="action"` for a primary marketplace conversion and `variant="primary"` for trust/navigation actions.

All overlays include Escape handling, focus containment, focus restoration, labelled dialog semantics, and scroll locking. All form controls expose label, hint, error, invalid, disabled, and focus states.

## Rules

- Extend an existing component before creating a near-duplicate.
- Never communicate backend failure as success or mock data.
- Display no more than two meaningful badges on an equipment card.
- Do not expose exact private addresses in discovery cards.
- Keep animation subtle and respect reduced-motion preferences.
- Use logical direction utilities such as `start`, `end`, `ms`, and `me` for RTL-safe layouts.
