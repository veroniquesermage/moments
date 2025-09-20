import {Injectable} from '@angular/core';
import {Router} from '@angular/router';
import {PersistenceService} from 'src/core/services/persistence.service';

@Injectable({ providedIn: 'root' })
export class GroupContextService{

  constructor(private router: Router,
              private persistenceService: PersistenceService) {
  }

  setGroupContext(id: number): void {
    try {
      // 1. Nettoyer le contexte précédent
      this.clearNavigationStates();

      // 2. Sauvegarder le nouveau groupId
      const safeId = Number(id);
      this.persistenceService.saveActiveGroupId(safeId);

      console.log(`[GroupContext] Contexte groupe ${safeId} défini (sans cache des membres)`);
    } catch (error) {
      console.error('[GroupContext] Erreur lors du changement de contexte:', error);
    }
  }

  getGroupId(): number | null {
    const id = this.persistenceService.getActiveGroupId();
    if (!id) {
      void this.router.navigate(['/groupe/onboarding']);
      return null;
    }
    return id;
  }

  clearGroupCache(){
    this.persistenceService.clearActiveGroupId();
    console.log('[GroupContext] Cache groupe nettoyé');
  }

  /**
   * Nettoyer les états de navigation lors du changement de groupe
   */
  private clearNavigationStates(): void {
    this.persistenceService.clearAllNavigationStates();
    console.log('[GroupContext] États de navigation nettoyés');
  }

}
