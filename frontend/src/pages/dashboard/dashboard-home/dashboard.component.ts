import {Component, OnInit} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {GroupContextService} from 'src/core/services/group-context.service';
import {GroupDetail} from 'src/core/models/group/group-detail.model';
import {AuthService} from 'src/security/service/auth.service';
import {ErrorService} from 'src/core/services/error.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit{

  selectedGroup: GroupDetail | undefined = undefined;
  isAdmin = false;
  isManagedTiers = false;
  loadingError = false;
  retryCount = 0;
  maxRetries = 3;

  constructor(
    public groupService: GroupService,
    public router: Router,
    public groupContextService: GroupContextService,
    private authService: AuthService,
    public errorService: ErrorService
  ) {
  }

  async ngOnInit() {
    await this.loadGroupDetail();
    if (this.authService.profile()?.isCompteTiers) {
      this.isManagedTiers = true;
    }

  }

  goToMesCadeaux() {
    void this.router.navigate(['dashboard', 'mes-cadeaux']);
  }


  goToListesMembres() {
    void this.router.navigate(['dashboard', 'leurs-cadeaux']);

  }

  goToSuiviCadeaux() {
    void this.router.navigate(['dashboard', 'cadeaux-suivis']);
  }

  goToIdeeCadeaux(){
    void this.router.navigate(['dashboard', 'idees']);
  }

  goToProfile() {
    void this.router.navigate(['profile']);
  }
  goToGestionGroupe() {
    void this.router.navigate(['/groupe/admin']);
  }

  goToComptesTiers() {
    void this.router.navigate(['/compte-tiers']);
  }

  goToTheme() {
    void this.router.navigate(['/theme']);
  }

  async switchToParent() {
    try{
      await this.authService.switchToParent();
      await this.loadGroupDetail();
      this.isManagedTiers = false;
    } catch (e) {
      this.errorService.showError("Une erreur s'est produite, veuillez réessayer.")
    }
  }

  async loadGroupDetail(){
    try {
      this.loadingError = false;
      const groupId = this.groupContextService.getGroupId();

      if (!groupId) {
        // Pas de groupe valide, arrêter ici car redirection en cours
        return;
      }

      const result = await this.groupService.getGroupDetail(groupId);

      if(result.success){
        this.selectedGroup = result.data;
        this.isAdmin = this.selectedGroup.role == 'ADMIN';
        this.retryCount = 0; // Reset sur succès
      } else {
        await this.handleLoadingError(result.message || "Erreur lors du chargement du groupe");
      }
    } catch (error) {
      await this.handleLoadingError("Erreur lors du chargement du groupe");
    }
  }

  private async handleLoadingError(message: string) {
    this.retryCount++;

    if (this.retryCount <= this.maxRetries) {
      console.info(`Tentative de rechargement automatique ${this.retryCount}/${this.maxRetries}`);
      // Retry automatique avec délai progressif
      const delay = this.retryCount * 1000; // 1s, 2s, 3s
      setTimeout(() => this.loadGroupDetail(), delay);
    } else {
      // Échec définitif après tous les retries
      this.loadingError = true;
      this.errorService.showError(`${message}. Veuillez rafraîchir la page.`);
    }
  }

  async manualRetry() {
    this.retryCount = 0; // Reset pour permettre nouveaux auto-retries
    await this.loadGroupDetail();
  }
}
