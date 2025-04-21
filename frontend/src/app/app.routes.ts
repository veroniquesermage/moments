import {Routes} from '@angular/router';
import {DashboardComponent} from 'src/pages/dashboard/dashboard.component';
import {OnboardingComponent} from 'src/pages/groupe/onboarding/onboarding.component';

export const routes: Routes = [
  {
    path: 'groupe/onboarding',
    component: OnboardingComponent,
  },
  {
    path: 'groupe/dashboard',
    component: DashboardComponent,
  },
  {
    path: '',
    redirectTo: 'groupe/onboarding',
    pathMatch: 'full',
  },
  {
    path: '**',
    redirectTo: 'groupe/onboarding',
  },
];




