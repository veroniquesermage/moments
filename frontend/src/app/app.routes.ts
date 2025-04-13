import {Routes} from '@angular/router';

export const routes: Routes = [{
  path: 'account',
  loadChildren: () =>
    import('./features/account/account.routes').then((m) => m.ACCOUNT_ROUTES),
},
  {
    path: 'app',
    loadComponent: () => import('./features/app/pages/app-home/app-home.component').then(m => m.AppHomeComponent),
  }];


