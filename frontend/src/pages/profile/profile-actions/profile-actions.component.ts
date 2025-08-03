import {Component} from '@angular/core';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
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

  constructor(private router: Router) {
  }

  async changeGroup() {
    await this.router.navigate(['/groupe/onboarding']);
  }

  async back() {
    await this.router.navigate(['/dashboard']);
  }

}
