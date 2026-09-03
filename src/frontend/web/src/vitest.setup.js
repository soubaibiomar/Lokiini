import '@testing-library/jest-dom/vitest';
import { cleanup } from '@testing-library/react';
import { afterEach, vi } from 'vitest';

afterEach(() => {
  cleanup();
  window.localStorage.clear();
  window.history.replaceState(null, '', '/');
});

globalThis.requestAnimationFrame = (callback) => globalThis.setTimeout(callback, 0);
globalThis.cancelAnimationFrame = (handle) => globalThis.clearTimeout(handle);
window.scrollTo = vi.fn();
window.matchMedia ||= vi.fn().mockImplementation((query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(),
  removeListener: vi.fn(),
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}));

