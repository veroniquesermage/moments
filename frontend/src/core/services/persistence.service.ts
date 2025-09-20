import { Injectable, signal } from '@angular/core';

/**
 * 🎯 PersistenceService MINIMALISTE
 *
 * Gère UNIQUEMENT :
 * - localStorage : groupId actif, préférences utilisateur (thème)
 * - sessionStorage : état navigation (position, filtres, scroll)
 *
 * NE gère JAMAIS :
 * - Cadeaux (toujours fresh)
 * - Membres (toujours fresh)
 * - Données business critiques
 */
@Injectable({
  providedIn: 'root'
})
export class PersistenceService {

  // Préfixes pour éviter les conflits
  private readonly LOCAL_PREFIX = 'app_kdo';
  private readonly SESSION_PREFIX = 'nav_state';

  // ============================================================================
  // 🏆 PERSISTENT DATA (localStorage) - Survit aux sessions
  // ============================================================================

  /**
   * Sauvegarder une donnée persistante (groupId, préférences)
   */
  savePersistent<T>(key: string, value: T): void {
    try {
      const fullKey = `${this.LOCAL_PREFIX}.${key}`;
      localStorage.setItem(fullKey, JSON.stringify(value));
    } catch (error) {
      console.warn('[PersistenceService] Erreur sauvegarde localStorage:', error);
    }
  }

  /**
   * Récupérer une donnée persistante
   */
  getPersistent<T>(key: string): T | null {
    try {
      const fullKey = `${this.LOCAL_PREFIX}.${key}`;
      const stored = localStorage.getItem(fullKey);
      return stored ? JSON.parse(stored) : null;
    } catch (error) {
      console.warn('[PersistenceService] Erreur lecture localStorage:', error);
      return null;
    }
  }

  /**
   * Supprimer une donnée persistante
   */
  removePersistent(key: string): void {
    try {
      const fullKey = `${this.LOCAL_PREFIX}.${key}`;
      localStorage.removeItem(fullKey);
    } catch (error) {
      console.warn('[PersistenceService] Erreur suppression localStorage:', error);
    }
  }

  // ============================================================================
  // 🎨 NAVIGATION STATE (sessionStorage) - État UI temporaire
  // ============================================================================

  /**
   * Sauvegarder l'état de navigation d'un composant
   */
  saveNavigationState<T>(componentKey: string, state: T): void {
    try {
      const fullKey = `${this.SESSION_PREFIX}.${componentKey}`;
      sessionStorage.setItem(fullKey, JSON.stringify({
        data: state,
        timestamp: Date.now()
      }));
    } catch (error) {
      console.warn('[PersistenceService] Erreur sauvegarde sessionStorage:', error);
    }
  }

  /**
   * Récupérer l'état de navigation d'un composant
   */
  getNavigationState<T>(componentKey: string, maxAge: number = 30 * 60 * 1000): T | null {
    try {
      const fullKey = `${this.SESSION_PREFIX}.${componentKey}`;
      const stored = sessionStorage.getItem(fullKey);

      if (!stored) return null;

      const parsed = JSON.parse(stored);
      const age = Date.now() - parsed.timestamp;

      // Vérifier l'âge (TTL)
      if (age > maxAge) {
        sessionStorage.removeItem(fullKey);
        return null;
      }

      return parsed.data;
    } catch (error) {
      console.warn('[PersistenceService] Erreur lecture sessionStorage:', error);
      return null;
    }
  }

  /**
   * Supprimer l'état de navigation d'un composant
   */
  removeNavigationState(componentKey: string): void {
    try {
      const fullKey = `${this.SESSION_PREFIX}.${componentKey}`;
      sessionStorage.removeItem(fullKey);
    } catch (error) {
      console.warn('[PersistenceService] Erreur suppression sessionStorage:', error);
    }
  }

  // ============================================================================
  // 🧹 NETTOYAGE
  // ============================================================================

  /**
   * Nettoyer TOUTES les données persistantes (logout)
   */
  clearAllPersistent(): void {
    try {
      // Nettoyer tous les items qui commencent par notre préfixe
      const keysToRemove: string[] = [];

      for (let i = 0; i < localStorage.length; i++) {
        const key = localStorage.key(i);
        if (key && key.startsWith(`${this.LOCAL_PREFIX}.`)) {
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach(key => localStorage.removeItem(key));

      console.log('[PersistenceService] Données persistantes nettoyées');
    } catch (error) {
      console.warn('[PersistenceService] Erreur nettoyage localStorage:', error);
    }
  }

  /**
   * Nettoyer TOUS les états de navigation (changement de groupe)
   */
  clearAllNavigationStates(): void {
    try {
      // Nettoyer tous les états de navigation
      const keysToRemove: string[] = [];

      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && key.startsWith(`${this.SESSION_PREFIX}.`)) {
          keysToRemove.push(key);
        }
      }

      keysToRemove.forEach(key => sessionStorage.removeItem(key));

      console.log('[PersistenceService] États de navigation nettoyés');
    } catch (error) {
      console.warn('[PersistenceService] Erreur nettoyage sessionStorage:', error);
    }
  }

  /**
   * Nettoyer les états expirés (maintenance)
   */
  cleanupExpiredStates(): void {
    try {
      const keysToRemove: string[] = [];
      const maxAge = 30 * 60 * 1000; // 30 minutes

      for (let i = 0; i < sessionStorage.length; i++) {
        const key = sessionStorage.key(i);
        if (key && key.startsWith(`${this.SESSION_PREFIX}.`)) {
          try {
            const stored = sessionStorage.getItem(key);
            if (stored) {
              const parsed = JSON.parse(stored);
              const age = Date.now() - parsed.timestamp;

              if (age > maxAge) {
                keysToRemove.push(key);
              }
            }
          } catch {
            // Item corrompu, le supprimer
            keysToRemove.push(key);
          }
        }
      }

      keysToRemove.forEach(key => sessionStorage.removeItem(key));

      if (keysToRemove.length > 0) {
        console.log(`[PersistenceService] ${keysToRemove.length} états expirés nettoyés`);
      }
    } catch (error) {
      console.warn('[PersistenceService] Erreur nettoyage états expirés:', error);
    }
  }

  // ============================================================================
  // 🎯 MÉTHODES SPÉCIALISÉES
  // ============================================================================

  /**
   * Gestion du GroupId actif
   */
  saveActiveGroupId(groupId: number): void {
    this.savePersistent('activeGroupId', groupId);
  }

  getActiveGroupId(): number | null {
    return this.getPersistent<number>('activeGroupId');
  }

  clearActiveGroupId(): void {
    this.removePersistent('activeGroupId');
  }

  /**
   * Gestion des préférences utilisateur
   */
  saveUserPreference<T>(key: string, value: T): void {
    this.savePersistent(`pref.${key}`, value);
  }

  getUserPreference<T>(key: string): T | null {
    return this.getPersistent<T>(`pref.${key}`);
  }

  /**
   * États de liste standard
   */
  saveListState(componentKey: string, state: ListNavigationState): void {
    this.saveNavigationState(componentKey, state);
  }

  getListState(componentKey: string): ListNavigationState | null {
    return this.getNavigationState<ListNavigationState>(componentKey);
  }
}

// ============================================================================
// 📋 INTERFACES
// ============================================================================

export interface ListNavigationState {
  currentPage: number;
  pageSize: number;
  filters?: Record<string, any>;
  sortBy?: string;
  sortDirection?: 'asc' | 'desc';
  scrollPosition?: number;
  searchQuery?: string;
}

export interface FormState {
  formData: Record<string, any>;
  isDirty: boolean;
  lastSaved: number;
}