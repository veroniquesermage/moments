import {Routes} from '@angular/router';
import {WelcomeComponent} from 'src/pages/welcome/welcome.component';

export const routes: Routes = [
  {
    path: '',
    component: WelcomeComponent,
  },
  {
    path: 'groupe',
    loadChildren: () => import('../pages/groupe/groupe.routes').then(m => m.groupeRoutes)
  },
  {
    path: 'dashboard',
    loadChildren: () => import('../pages/dashboard/dashboard.routes').then(m => m.dashboardRoutes)
  },
  {
    path: 'profile',
    loadChildren: () => import('../pages/profile/profile.routes').then(m => m.profileRoutes)
  },
  {
    path: '**',
    redirectTo: '',
  },
];




