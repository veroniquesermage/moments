import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {AuthService} from '../../../security/service/auth.service';

@Component({
  selector: 'app-profile-actions',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './profile-actions.component.html',
  styleUrl: './profile-actions.component.scss'
})
export class ProfileActionsComponent {

  constructor(private router: Router, private authService: AuthService) {
  }

  async changeGroup() {
    await this.router.navigate(['/groupe/onboarding']);
  }

  async back() {
    await this.router.navigate(['/dashboard']);
  }

  async logout() {
    await this.authService.logout();
  }

}
