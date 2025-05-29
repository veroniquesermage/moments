import {Component, effect, inject, Injector, runInInjectionContext} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AuthService} from 'src/security/service/auth.service';
import {GroupService} from 'src/core/services/group.service';
import {Router, RouterOutlet} from '@angular/router';
import {GroupStateService} from 'src/core/services/group-state.service';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';

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
    private groupStateService: GroupStateService,
    public errorService: ErrorService
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

    const result = await this.groupService.fetchGroups();

    if (result.success) {
      if (result.data.length === 1) {
        this.groupStateService.setSelectedGroup(result.data.at(0)!);
        await this.router.navigate(['/dashboard']);
      } else {
        await this.router.navigate(['/groupe/onboarding']);
      }
    } else {
      console.warn('⚠️ Impossible de charger les groupes :', result.message);
      this.errorService.showError('⚠️ Impossible de charger les groupes, veuillez essayer plus tard');
    }

    this.groupService.isLoading.set(false);
  }
}

