import {Component, effect, inject, Injector, runInInjectionContext, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AuthService} from 'src/security/service/auth.service';
import {GroupService} from 'src/core/services/group.service';
import {Router, RouterOutlet} from '@angular/router';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GroupContextService} from 'src/core/services/group-context.service';
import {ThemeService} from 'src/core/services/theme.service';
import {GlobalHeaderContextComponent} from 'src/shared/components/global-header-context/global-header-context.component';
import {GlobalToastrComponent} from 'src/shared/components/global-toastr/global-toastr.component';
import {GlobalFooterComponent} from 'src/shared/components/global-footer/global-footer.component';
import {ContextBannerService} from 'src/core/services/context-banner.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [
    CommonModule,
    RouterOutlet,
    TerminalModalComponent,
    GlobalHeaderContextComponent,
    GlobalToastrComponent,
    GlobalFooterComponent,
  ],
  templateUrl: './app.component.html',
})
export class AppComponent {

  offset = signal(0);
  private headerHeight = signal(0);
  private toastHeight = signal(0);

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

      this.watchCompteTiersStatus();
    });

  }

  private watchCompteTiersStatus() {
    const banner = inject(ContextBannerService);
    effect(() => {
      const user = this.auth.profile();
      const isTiers = !!user?.isCompteTiers;
      document.body.classList.toggle('compte-tiers', isTiers);
      if (isTiers) {
        banner.show('Connecté en tant que compte tiers');
      } else {
        banner.clear();
      }
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
        await this.groupContext.setGroupContext(result.data.at(0)?.id!);
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

  updateHeaderHeight(h: number) {
    this.headerHeight.set(h);
    this.computeOffset();
  }

  updateToastrHeight(h: number) {
    this.toastHeight.set(h);
    this.computeOffset();
  }

  private computeOffset() {
    this.offset.set(this.headerHeight() + this.toastHeight());
  }

}

