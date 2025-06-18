import { Component } from '@angular/core';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {ThemeService, Theme} from 'src/core/services/theme.service';

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

  get themes(): Theme[] {
    return [
      this.theme.current,
      ...this.theme.availableThemes.filter(t => t !== this.theme.current)
    ];
  }

  async changeGroup() {
    await this.router.navigate(['/groupe/onboarding']);
  }
}
