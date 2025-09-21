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
    // Initialisation immédiate des valeurs selon la taille actuelle
    this.initializeBreakpoints();

    // Observer mobile breakpoint
    this.breakpointObserver.observe(['(max-width: 767px)']).subscribe(result => {
      if (result.matches) {
        console.log('[ResponsiveService] Switching to MOBILE');
        this.isMobile.set(true);
        this.isTablet.set(false);
        this.isDesktop.set(false);
      }
    });

    // Observer tablet breakpoint
    this.breakpointObserver.observe(['(min-width: 768px) and (max-width: 1024px)']).subscribe(result => {
      if (result.matches) {
        console.log('[ResponsiveService] Switching to TABLET');
        this.isMobile.set(false);
        this.isTablet.set(true);
        this.isDesktop.set(false);
      }
    });

    // Observer desktop breakpoint
    this.breakpointObserver.observe(['(min-width: 1025px)']).subscribe(result => {
      if (result.matches) {
        console.log('[ResponsiveService] Switching to DESKTOP');
        this.isMobile.set(false);
        this.isTablet.set(false);
        this.isDesktop.set(true);
      }
    });
  }

  private initializeBreakpoints(): void {
    const width = window.innerWidth;
    console.log('[ResponsiveService] Window width at init:', width);

    if (width <= 767) {
      this.isMobile.set(true);
      this.isTablet.set(false);
      this.isDesktop.set(false);
    } else if (width <= 1024) {
      this.isMobile.set(false);
      this.isTablet.set(true);
      this.isDesktop.set(false);
    } else {
      this.isMobile.set(false);
      this.isTablet.set(false);
      this.isDesktop.set(true);
    }
  }

  /**
   * Retourne la taille de page appropriée selon l'écran actuel
   */
  getCurrentPageSize(): number {
    const pageSize = this.isMobile() ? PAGE_SIZES.mobile :
                     this.isTablet() ? PAGE_SIZES.tablet :
                     PAGE_SIZES.desktop;
    console.log('[ResponsiveService] getCurrentPageSize:', pageSize, 'Mobile:', this.isMobile(), 'Tablet:', this.isTablet(), 'Desktop:', this.isDesktop());
    return pageSize;
  }

  /**
   * Retourne la taille de page pour un contexte spécifique
   */
  getPageSizeForContext(context: keyof typeof PAGINATION_CONFIGS): number {
    const config = PAGINATION_CONFIGS[context] || PAGINATION_CONFIGS.default;
    const pageSize = this.isMobile() ? config.mobile : config.desktop;
    console.log('[ResponsiveService] getPageSizeForContext:', context, 'PageSize:', pageSize, 'Mobile:', this.isMobile());
    return pageSize;
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
