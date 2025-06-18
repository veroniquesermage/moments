import { Component } from '@angular/core';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {ThemeService} from 'src/core/services/theme.service';

@Component({
  selector: 'app-profile-actions',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './profile-actions.component.html',
  styleUrl: './profile-actions.component.scss'
})
export class ProfileActionsComponent {

  constructor(private router: Router, public theme: ThemeService) {
  }

  async changeGroup() {
    await this.router.navigate(['/groupe/onboarding']);
  }
}
