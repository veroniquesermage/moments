import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute } from '@angular/router';
import { AuthService } from 'src/security/service/auth.service';
import { ErrorService } from 'src/core/services/error.service';
import { RegisterRequest } from 'src/security/model/register-request.model';
import { TerminalModalComponent } from 'src/shared/components/terminal-modal/terminal-modal.component';
import { FeedbackTestComponent } from 'src/shared/components/feedback-test/feedback-test.component';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, TerminalModalComponent, FeedbackTestComponent],
  templateUrl: './register.component.html',
  styleUrl: './register.component.scss'
})
export class RegisterComponent {
  prenom = '';
  nom = '';
  email: string | null = null;
  password: string | null = null;
  stayLoggedIn = false;
  composant: string = 'RegisterComponent';

  constructor(private route: ActivatedRoute,
              private auth: AuthService,
              public errorService: ErrorService) {
    this.route.queryParams.subscribe(params => {
      this.email = params['email'] ?? null;
      this.password = params['password'] ?? null;
      this.stayLoggedIn = params['rememberMe'] === 'true';
    });
  }

  async submit(): Promise<void> {
    const payload: RegisterRequest = {
      prenom: this.prenom,
      nom: this.nom,
      email: this.email || undefined,
      password: this.password || undefined,
      rememberMe: this.stayLoggedIn
    };
    const result = await this.auth.register(payload);
    if (!result.success) {
      this.errorService.showError(result.message);
    }
  }
}
