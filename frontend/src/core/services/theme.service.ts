import { Injectable } from '@angular/core';

export type Theme = 'dark' | 'light' | 'daltonien' | 'neuroatypique';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly storageKey = 'ui-theme';
  current: Theme = 'dark';
  readonly availableThemes: Theme[] = ['dark', 'light', 'daltonien', 'neuroatypique'];

  constructor() {
    const stored = localStorage.getItem(this.storageKey) as Theme | null;
    if (this.availableThemes.includes(stored as Theme)) {
      this.current = stored as Theme;
    }
    this.applyTheme();
  }

  setTheme(theme: Theme) {
    if (this.availableThemes.includes(theme)) {
      this.current = theme;
      localStorage.setItem(this.storageKey, this.current);
      this.applyTheme();
    }
  }

  toggleTheme() {
    const idx = this.availableThemes.indexOf(this.current);
    const next = this.availableThemes[(idx + 1) % this.availableThemes.length];
    this.setTheme(next);
  }

  private applyTheme() {
    const body = document.body;
    const themes = ['light', 'daltonien', 'neuroatypique', 'darkpastel']; // à compléter
    themes.forEach(t => body.classList.remove(`${t}-theme`));
    body.classList.add(`${this.current}-theme`);

  }
}
