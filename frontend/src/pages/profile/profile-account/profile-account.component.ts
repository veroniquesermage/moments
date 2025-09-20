import {Component, OnInit, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {User} from 'src/security/model/user.model';
import {ErrorService} from 'src/core/services/error.service';
import {AuthService} from 'src/security/service/auth.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-profile-account',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './profile-account.component.html',
  styleUrl: './profile-account.component.scss'
})
export class ProfileAccountComponent implements OnInit{

  user = signal<User | null>(null);
  isLoading = signal<boolean>(false);

  constructor(public errorService: ErrorService,
              private authService: AuthService,
              public router: Router) {
  }

  async ngOnInit() {
    await this.loadUserProfile();
  }

  private async loadUserProfile(): Promise<void> {
    // 1. Essayer d'abord avec le signal du AuthService
    let userProfile = this.authService.profile();

    if (userProfile) {
      console.log('[ProfileAccount] Profil trouvé dans AuthService:', userProfile);
      this.user.set(userProfile);
      return;
    }

    // 2. Si pas de profil, faire un fetch depuis le backend
    console.log('[ProfileAccount] Aucun profil en cache, fetch depuis le backend...');
    this.isLoading.set(true);

    try {
      userProfile = await this.authService.getCurrentUser();
      if (userProfile) {
        console.log('[ProfileAccount] Profil récupéré depuis le backend:', userProfile);
        this.user.set(userProfile);
      } else {
        console.error('[ProfileAccount] Aucun profil récupéré');
        this.errorService.showError("❌ Impossible d'afficher les infos de ce membre. Veuillez réessayer plus tard.");
      }
    } catch (error) {
      console.error('[ProfileAccount] Erreur lors du fetch du profil:', error);
      this.errorService.showError("❌ Erreur lors du chargement du profil utilisateur.");
    } finally {
      this.isLoading.set(false);
    }
  }

  async disconnect() {
    await this.authService.logout()
  }

  changePassword() {
    void this.router.navigate(['/auth/reset-password'], {
      queryParams: {context: 'change'}
    });
  }
}
