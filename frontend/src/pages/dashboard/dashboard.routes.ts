import {Routes} from '@angular/router';
import {DashboardComponent} from './dashboard-home/dashboard.component';

export const dashboardRoutes: Routes = [
  {
    path: '',
    component: DashboardComponent,
    title: 'Dashboard'
  },
  // Tu pourras ajouter ici les sous-routes comme :
  // { path: 'cadeaux', loadComponent: () => import('./cadeaux/mes-cadeaux.component').then(c => c.MesCadeauxComponent) }
];
