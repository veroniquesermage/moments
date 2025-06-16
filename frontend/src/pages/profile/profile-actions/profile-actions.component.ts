import { Component } from '@angular/core';
import {Router} from '@angular/router';

@Component({
  selector: 'app-profile-actions',
  standalone: true,
  imports: [],
  templateUrl: './profile-actions.component.html',
  styleUrl: './profile-actions.component.scss'
})
export class ProfileActionsComponent {

  constructor(private router: Router) {
  }

  async changeGroup() {
    await this.router.navigate(['/groupe/onboarding']);
  }
}
