import { Injectable, signal } from '@angular/core';
import { PersistenceService } from 'src/core/services/persistence.service';

export const AVAILABLE_THEMES = [
  'dark',
  'light',
  'daltonien',
  'neuroatypique'
] as const;

export type Theme = typeof AVAILABLE_THEMES[number];

@Injectable({ providedIn: 'root' })
export class ThemeService {
  // Signal réactif pour le thème actuel
  current = signal<Theme>('dark');

  constructor(private persistenceService: PersistenceService) {
    this.initializeFromStorage();
  }

  /**
   * Initialiser le thème depuis le storage
   */
  private initializeFromStorage(): void {
    const stored = this.persistenceService.getUserPreference<Theme>('theme');
    if (stored && AVAILABLE_THEMES.includes(stored)) {
      this.current.set(stored);
    }
    this.applyTheme();
  }

  setTheme(theme: Theme) {
    if (AVAILABLE_THEMES.includes(theme)) {
      this.current.set(theme);
      this.persistenceService.saveUserPreference('theme', theme);
      this.applyTheme();
      console.log(`[ThemeService] Thème changé vers: ${theme}`);
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
    body.classList.add(`${this.current()}-theme`);
  }
}
