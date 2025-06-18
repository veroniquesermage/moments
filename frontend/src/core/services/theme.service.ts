import { Injectable } from '@angular/core';

export type Theme = 'dark' | 'light';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private readonly storageKey = 'ui-theme';
  current: Theme = 'dark';

  constructor() {
    const stored = localStorage.getItem(this.storageKey) as Theme | null;
    if (stored === 'light') {
      this.current = stored;
    }
    this.applyTheme();
  }

  toggleTheme() {
    this.current = this.current === 'dark' ? 'light' : 'dark';
    localStorage.setItem(this.storageKey, this.current);
    this.applyTheme();
  }

  private applyTheme() {
    const body = document.body;
    if (this.current === 'light') {
      body.classList.add('light-theme');
    } else {
      body.classList.remove('light-theme');
    }
  }
}
