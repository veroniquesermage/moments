// group-routing.module.ts
import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {OnboardingComponent} from 'src/pages/groupe/onboarding/onboarding.component';
import {DashboardComponent} from 'src/pages/dashboard/dashboard.component';

const routes: Routes = [
  {path: 'onboarding', component: OnboardingComponent},
  {path: 'dashboard', component: DashboardComponent},
  {path: '', redirectTo: 'onboarding', pathMatch: 'full'},
  {path: '**', redirectTo: ''}
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class GroupRoutingModule {
}
