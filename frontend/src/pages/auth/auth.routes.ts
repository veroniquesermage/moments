import {Routes} from '@angular/router';
import {CompleteProfileComponent} from 'src/pages/auth/complete-profile/complete-profile.component';
import {ResetPasswordComponent} from 'src/pages/auth/reset-password/reset-password.component';

export const authRoutes: Routes = [
  {
    path: 'initialiser',
    component: CompleteProfileComponent,
    data: { public: true }
  },
  {
    path: 'reset-password',
    component: ResetPasswordComponent,
    data: { public: true }
  }
];
