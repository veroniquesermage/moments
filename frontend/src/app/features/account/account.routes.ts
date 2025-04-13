import {Routes} from '@angular/router';
import {ConnexionComponent} from './pages/connexion/connexion.component';
import {CreateGroupComponent} from 'src/app/features/account/pages/create-group/create-group.component';
import {ChooseGroupComponent} from 'src/app/features/account/pages/choose-group/choose-group.component';

export const ACCOUNT_ROUTES: Routes = [
  {path: '', component: ConnexionComponent},
  {path: 'create', component: CreateGroupComponent},
  {path: 'choose', component: ChooseGroupComponent}
];

