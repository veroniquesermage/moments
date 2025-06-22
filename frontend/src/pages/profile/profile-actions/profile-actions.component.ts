import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {Theme, ThemeService} from 'src/core/services/theme.service';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';

@Component({
  selector: 'app-profile-actions',
  standalone: true,
  imports: [CommonModule, FeedbackTestComponent],
  templateUrl: './profile-actions.component.html',
  styleUrl: './profile-actions.component.scss'
})
export class ProfileActionsComponent {
  composant: string = "ProfileActionsComponent";

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

  async back() {
    await this.router.navigate(['/dashboard']);
  }

}
