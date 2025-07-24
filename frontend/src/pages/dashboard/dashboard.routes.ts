import {Routes} from '@angular/router';
import {DashboardComponent} from './dashboard-home/dashboard.component';
import {UserGiftsComponent} from 'src/pages/dashboard/mes-cadeaux/user-gifts/user-gifts.component';
import {GiftCreateComponent} from 'src/pages/dashboard/mes-cadeaux/gift-create/gift-create.component';
import {GiftDetailPageComponent} from 'src/pages/dashboard/shared/gift-detail-page/gift-detail-page.component';
import {GiftUpdateComponent} from 'src/pages/dashboard/mes-cadeaux/gift-update/gift-update.component';
import {
  GroupMemberGiftsComponent
} from 'src/pages/dashboard/cadeaux-membres/group-member-gifts/group-member-gifts.component';
import {
  MyGiftsFollowUpComponent
} from 'src/pages/dashboard/suivi-cadeaux-reserves/my-gifts-follow-up/my-gifts-follow-up.component';
import {GiftDeliverComponent} from 'src/pages/dashboard/suivi-cadeaux-reserves/gift-deliver/gift-deliver.component';
import {GiftSharingComponent} from 'src/pages/dashboard/sharing/gift-sharing/gift-sharing.component';
import {MyGiftsIdeasComponent} from 'src/pages/dashboard/gift-ideas/my-gifts-ideas/my-gifts-ideas.component';
import {IdeasCreateComponent} from 'src/pages/dashboard/gift-ideas/ideas-create/ideas-create.component';
import {IdeasUpdateComponent} from 'src/pages/dashboard/gift-ideas/ideas-update/ideas-update.component';
import {ManagedAccountsComponent} from 'src/pages/compte-tiers/managed-accounts/managed-accounts.component';

export const dashboardRoutes: Routes = [
  { path: '', component: DashboardComponent},
  { path: 'mes-cadeaux', component: UserGiftsComponent},
  { path: 'mes-cadeaux/creer', component: GiftCreateComponent},
  { path: 'mes-cadeaux/modifier/:id', component: GiftUpdateComponent, data: { context: 'mes-cadeaux' } },
  { path: 'leurs-cadeaux', component: GroupMemberGiftsComponent},
  { path: 'cadeaux-suivis', component: MyGiftsFollowUpComponent},
  { path: 'cadeaux-suivis/livraison/:id', component: GiftDeliverComponent},
  { path: 'partage/:id', component: GiftSharingComponent},
  { path: 'cadeau/:id', component: GiftDetailPageComponent },
  { path: 'idees', component: MyGiftsIdeasComponent },
  { path: 'idees/creer', component: IdeasCreateComponent},
  { path: 'idees/modifier/:id', component: IdeasUpdateComponent},
  { path: 'comptes-tiers', component: ManagedAccountsComponent},
];
