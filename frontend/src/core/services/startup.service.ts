import {Injectable} from '@angular/core';
import {TokenService} from 'src/security/service/token.service';
import {AuthService} from 'src/security/service/auth.service';
import {Router} from '@angular/router';
import {firstValueFrom} from 'rxjs';

@Injectable({providedIn: 'root'})
export class StartupService {
  constructor(
    private tokenService: TokenService,
    private authService: AuthService,
    private router: Router
  ) {}

  async handleAppStartup(): Promise<void> {

    console.log('✅ StartupService exécuté');
    const isExpired = this.tokenService.isTokenExpired();
    const rememberMe = this.tokenService.hasRememberMe();

    if (!isExpired) {
      if (this.router.url === '/') {
        await this.redirectToCorrectPage();
      }
      return;
    }

    if (rememberMe) {
      try {
        await firstValueFrom(this.authService.refreshToken());
        await this.redirectToCorrectPage();

      } catch (error) {
        this.tokenService.clear();
        void this.router.navigate(['/']);
      }
    } else {
      this.tokenService.clear();
      void this.router.navigate(['/']);
    }
  }

  private async redirectToCorrectPage(): Promise<void> {
    const groupId = localStorage.getItem('current_group_id');

    if (groupId) {
      await this.router.navigate(['/dashboard']);
    } else {
      await this.router.navigate(['/groupe/onboarding']);
    }
  }
}
