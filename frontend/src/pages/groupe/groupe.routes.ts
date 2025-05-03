import {Routes} from '@angular/router';
import {OnboardingComponent} from './onboarding/onboarding.component';
import {GroupCreateComponent} from './group-create/group-create.component';
import {GroupJoinComponent} from './group-join/group-join.component';

export const groupeRoutes: Routes = [
  {path: 'onboarding', component: OnboardingComponent},
  {path: 'onboarding/creer', component: GroupCreateComponent},
  {path: 'onboarding/rejoindre', component: GroupJoinComponent},
  {path: '', redirectTo: 'onboarding', pathMatch: 'full'}
];
