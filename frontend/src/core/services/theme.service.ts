import { Injectable } from '@angular/core';

export type Theme = 'dark' | 'light' | 'daltonien';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly storageKey = 'ui-theme';
  current: Theme = 'dark';
  readonly availableThemes: Theme[] = ['dark', 'light', 'daltonien'];

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
    body.classList.remove('light-theme', 'daltonien-theme');
    if (this.current === 'light') {
      body.classList.add('light-theme');
    } else if (this.current === 'daltonien') {
      body.classList.add('daltonien-theme');
    }
  }
}
