import {Routes} from '@angular/router';
import {CompleteProfileComponent} from 'src/pages/auth/complete-profile/complete-profile.component';

export const authRoutes: Routes = [
  {
    path: 'initialiser',
    component: CompleteProfileComponent
  }
];
