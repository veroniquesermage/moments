import {Routes} from '@angular/router';
import {DashboardComponent} from './dashboard-home/dashboard.component';
import {GroupCreateComponent} from 'src/pages/groupe/group-create/group-create.component';
import {UserGiftsComponent} from 'src/pages/dashboard/user-gifts/user-gifts.component';
import {GiftCreateComponent} from 'src/pages/dashboard/gift-create/gift-create.component';

export const dashboardRoutes: Routes = [
  {path: '', component: DashboardComponent},
  {path: 'mes-cadeaux', component: UserGiftsComponent},
  {path: 'mes-cadeaux/creer', component: GiftCreateComponent},
];
