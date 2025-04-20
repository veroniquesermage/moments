import {Routes} from '@angular/router';
import {DashboardComponent} from 'src/pages/dashboard/dashboard.component';
import {OnboardingComponent} from 'src/pages/groupe/onboarding/onboarding.component';

export const routes: Routes = [
  {
    path: 'groupes/onboarding',
    component: OnboardingComponent,
  },
  {
    path: 'groupes/dashboard',
    component: DashboardComponent,
  },
  {
    path: '',
    redirectTo: 'groupes/onboarding',
    pathMatch: 'full',
  },
  {
    path: '**',
    redirectTo: 'groupes/onboarding',
  },
];




