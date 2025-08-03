import {Routes} from '@angular/router';
import {WelcomeComponent} from 'src/pages/auth/welcome/welcome.component';
import {ThemeComponent} from 'src/pages/theme/theme.component';

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
    path: 'auth',
    loadChildren: () => import('../pages/auth/auth.routes').then(m => m.authRoutes)
  },
  {
    path: 'compte-tiers',
    loadChildren: () => import('../pages/compte-tiers/compte-tiers.routes').then(m => m.compteTiersRoutes)
  },
  {
    path: 'theme',
    component: ThemeComponent
  },
  {
    path: '**',
    redirectTo: '/404',
  },
];




