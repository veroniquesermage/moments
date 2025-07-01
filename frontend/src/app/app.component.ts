import {Component, effect, inject, Injector, runInInjectionContext} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AuthService} from 'src/security/service/auth.service';
import {GroupService} from 'src/core/services/group.service';
import {Router, RouterOutlet} from '@angular/router';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GroupContextService} from 'src/core/services/group-context.service';
import {ThemeService} from 'src/core/services/theme.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, RouterOutlet, TerminalModalComponent],
  templateUrl: './app.component.html',
})
export class AppComponent {

  constructor(
    public auth: AuthService,
    private groupService: GroupService,
    private router: Router,
    private groupContext: GroupContextService,
    public errorService: ErrorService,
    // ensure theme is initialized on app startup
    private _theme: ThemeService
  ) {
    const injector = inject(Injector);
    runInInjectionContext(injector, () => this.initEffects());
  }

  private initEffects() {
    const injector = inject(Injector);

    runInInjectionContext(injector, () => {
      const auth = inject(AuthService);

      effect(() => {
        if (auth.isLoggedIn()) {
          this.loadGroupsAfterLogin();
        }
      });
    });
  }

  private async loadGroupsAfterLogin() {
    this.groupService.isLoading.set(true);
    const inviteCode = localStorage.getItem('app_kdo.codeInvit');

    if (inviteCode) {
      if (!this.router.url.startsWith('/groupe/onboarding/rejoindre')) {
        await this.router.navigateByUrl(`/groupe/onboarding/rejoindre?inviteCode=${inviteCode}`);
      }
      return;
    }

    const result = await this.groupService.fetchGroups();

    if (result.success) {
      if (result.data.length === 1) {
        this.groupContext.setGroupContext(result.data.at(0)?.id!);
        if (!this.router.url.startsWith('/dashboard')) {
          await this.router.navigate(['/dashboard']);
        }
      } else {
        if (!this.router.url.startsWith('/groupe/onboarding')) {
          await this.router.navigate(['/groupe/onboarding']);
        }
      }
    } else {
      console.warn('⚠️ Impossible de charger les groupes :', result.message);
      this.errorService.showError('⚠️ Impossible de charger les groupes, veuillez essayer plus tard');
    }

    this.groupService.isLoading.set(false);
  }

}

