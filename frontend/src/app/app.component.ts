import {Component, effect, inject, Injector, runInInjectionContext} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AuthService} from 'src/security/service/auth.service';
import {GroupService} from 'src/core/services/groupe.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './app.component.html',
})
export class AppComponent {
  constructor(
    public auth: AuthService,
    private groupService: GroupService,
    private router: Router
  ) {
    const injector = inject(Injector);
    runInInjectionContext(injector, () => this.initEffects());
  }

  private initEffects() {
    const auth = inject(AuthService);
    effect(() => {
      if (this.auth.isLoggedIn()) {
        this.groupService.fetchGroups().then(groupList => {
          if (groupList.length === 1) {
            this.router.navigate(['groupe', 'dashboard']);
          } else {
            this.router.navigate(['groupe', 'onboarding']);
          }
        });
      }
    });
  }
}

