import { Injectable, signal, inject } from '@angular/core';
import { BreakpointObserver } from '@angular/cdk/layout';

/**
 * Configuration des tailles de page par breakpoint
 */
const PAGE_SIZES = {
  mobile: 4,     // Écrans < 768px
  tablet: 12,    // Écrans 768px - 1024px
  desktop: 20    // Écrans > 1024px
} as const;

/**
 * Configuration spécifique par contexte de pagination
 */
const PAGINATION_CONFIGS = {
  'user-gifts': { mobile: 4, desktop: 20 },
  'member-gifts': { mobile: 4, desktop: 15 },
  'followed-gifts': { mobile: 4, desktop: 25 },
  'default': { mobile: 4, desktop: 20 }
} as const;

/**
 * Service pour gérer la pagination responsive selon la taille d'écran
 */
@Injectable({ providedIn: 'root' })
export class ResponsiveService {
  private breakpointObserver = inject(BreakpointObserver);

  isMobile = signal(false);
  isTablet = signal(false);
  isDesktop = signal(true);

  constructor() {
    // Détection mobile (< 768px)
    this.breakpointObserver.observe(['(max-width: 767px)']).subscribe(result => {
      this.isMobile.set(result.matches);
      if (result.matches) {
        this.isTablet.set(false);
        this.isDesktop.set(false);
      }
    });

    // Détection tablet (768px - 1024px)
    this.breakpointObserver.observe(['(min-width: 768px) and (max-width: 1024px)']).subscribe(result => {
      this.isTablet.set(result.matches);
      if (result.matches) {
        this.isMobile.set(false);
        this.isDesktop.set(false);
      }
    });

    // Détection desktop (> 1024px)
    this.breakpointObserver.observe(['(min-width: 1025px)']).subscribe(result => {
      this.isDesktop.set(result.matches);
      if (result.matches) {
        this.isMobile.set(false);
        this.isTablet.set(false);
      }
    });
  }

  /**
   * Retourne la taille de page appropriée selon l'écran actuel
   */
  getCurrentPageSize(): number {
    if (this.isMobile()) return PAGE_SIZES.mobile;
    if (this.isTablet()) return PAGE_SIZES.tablet;
    return PAGE_SIZES.desktop;
  }

  /**
   * Retourne la taille de page pour un contexte spécifique
   */
  getPageSizeForContext(context: keyof typeof PAGINATION_CONFIGS): number {
    const config = PAGINATION_CONFIGS[context] || PAGINATION_CONFIGS.default;
    return this.isMobile() ? config.mobile : config.desktop;
  }

  /**
   * Retourne le breakpoint actuel sous forme de string
   */
  getCurrentBreakpoint(): 'mobile' | 'tablet' | 'desktop' {
    if (this.isMobile()) return 'mobile';
    if (this.isTablet()) return 'tablet';
    return 'desktop';
  }
}
