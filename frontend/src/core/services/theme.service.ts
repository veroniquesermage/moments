import { Injectable } from '@angular/core';

export const AVAILABLE_THEMES = [
  'dark',
  'light',
  'daltonien',
  'neuroatypique'
] as const;

export type Theme = typeof AVAILABLE_THEMES[number];

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly storageKey = 'ui-theme';
  current: Theme = 'dark';

  constructor() {
    const stored = localStorage.getItem(this.storageKey) as Theme | null;
    if (stored && AVAILABLE_THEMES.includes(stored)) {
      this.current = stored;
    }
    this.applyTheme();
  }

  setTheme(theme: Theme) {
    if (AVAILABLE_THEMES.includes(theme)) {
      this.current = theme;
      localStorage.setItem(this.storageKey, theme);
      this.applyTheme();
    }
  }

/*  toggleTheme() {
    const idx = AVAILABLE_THEMES.indexOf(this.current);
    const next = AVAILABLE_THEMES[(idx + 1) % AVAILABLE_THEMES.length];
    this.setTheme(next);
  }*/

  get availableThemes(): Theme[] {
    return [...AVAILABLE_THEMES];
  }

  private applyTheme() {
    const body = document.body;
    AVAILABLE_THEMES.forEach(t => body.classList.remove(`${t}-theme`));
    body.classList.add(`${this.current}-theme`);
  }
}
