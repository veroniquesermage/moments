import {Routes} from '@angular/router';
import {DashboardComponent} from './dashboard-home/dashboard.component';
import {UserGiftsComponent} from 'src/pages/dashboard/user-gifts/user-gifts.component';
import {GiftCreateComponent} from 'src/pages/dashboard/gift-create/gift-create.component';
import {GiftDetailPageComponent} from 'src/pages/dashboard/gift-detail-page/gift-detail-page.component';
import {GiftUpdateComponent} from 'src/pages/dashboard/gift-update/gift-update.component';
import {GroupMemberGiftsComponent} from 'src/pages/dashboard/group-member-gifts/group-member-gifts.component';
import {TakeGiftComponent} from 'src/pages/dashboard/take-gift/take-gift.component';

export const dashboardRoutes: Routes = [
  {path: '', component: DashboardComponent},
  {path: 'mes-cadeaux', component: UserGiftsComponent},
  {path: 'mes-cadeaux/creer', component: GiftCreateComponent},
  { path: 'mes-cadeaux/:id', component: GiftDetailPageComponent, data: { context: 'own' } },
  { path: 'membre/:membreId/cadeaux/:id', component: GiftDetailPageComponent, data: { context: 'other' } },
  { path: 'mes-cadeaux/modifier/:id', component: GiftUpdateComponent, data: { context: 'own' } },
  { path: 'leurs-cadeaux', component: GroupMemberGiftsComponent},
  { path: 'leurs-cadeaux/:id', component: GiftDetailPageComponent, data: { context: 'other' } },
  { path: 'leurs-cadeaux/:id/prendre', component: TakeGiftComponent},

];
