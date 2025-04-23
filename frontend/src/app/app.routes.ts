import {Routes} from '@angular/router';
import {DashboardComponent} from 'src/pages/dashboard/dashboard.component';
import {OnboardingComponent} from 'src/pages/groupe/onboarding/onboarding.component';
import {WelcomeComponent} from 'src/pages/welcome/welcome.component';
import {GroupCreateComponent} from 'src/pages/groupe/group-create/group-create.component';
import {GroupJoinComponent} from 'src/pages/groupe/group-join/group-join.component';

export const routes: Routes = [
  {
    path: '',
    component: WelcomeComponent,
  },
  {
    path: 'groupe/onboarding',
    component: OnboardingComponent,
  },
  {
    path: 'groupe/dashboard',
    component: DashboardComponent,
  },
  {
    path: 'groupe/onboarding/creer',
    component: GroupCreateComponent,
  },
  {
    path: 'groupe/onboarding/rejoindre',
    component: GroupJoinComponent,
  },
  {
    path: '**',
    redirectTo: '',
  },
];




