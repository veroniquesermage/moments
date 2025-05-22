import {Routes} from '@angular/router';
import {DashboardComponent} from './dashboard-home/dashboard.component';
import {UserGiftsComponent} from 'src/pages/dashboard/mes-cadeaux/user-gifts/user-gifts.component';
import {GiftCreateComponent} from 'src/pages/dashboard/mes-cadeaux/gift-create/gift-create.component';
import {GiftDetailPageComponent} from 'src/pages/dashboard/shared/gift-detail-page/gift-detail-page.component';
import {GiftUpdateComponent} from 'src/pages/dashboard/mes-cadeaux/gift-update/gift-update.component';
import {
  GroupMemberGiftsComponent
} from 'src/pages/dashboard/cadeaux-membres/group-member-gifts/group-member-gifts.component';
import {TakeGiftComponent} from 'src/pages/dashboard/cadeaux-membres/take-gift/take-gift.component';
import {
  MyGiftsFollowUpComponent
} from 'src/pages/dashboard/suivi-cadeaux-reserves/my-gifts-follow-up/my-gifts-follow-up.component';
import {
  GiftFollowUpDetailComponent
} from 'src/pages/dashboard/suivi-cadeaux-reserves/gift-follow-up-detail/gift-follow-up-detail.component';
import {GiftDeliverComponent} from 'src/pages/dashboard/suivi-cadeaux-reserves/gift-deliver/gift-deliver.component';

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
  { path: 'cadeaux-suivis', component: MyGiftsFollowUpComponent},
  { path: 'cadeaux-suivis/detail/:id', component: GiftFollowUpDetailComponent},
  { path: 'cadeaux-suivis/livraison/:id', component: GiftDeliverComponent},

];
