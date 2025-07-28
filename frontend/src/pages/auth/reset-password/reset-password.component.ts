import {Component, inject, OnInit, signal} from '@angular/core';
import {FeedbackTestComponent} from "src/shared/components/feedback-test/feedback-test.component";
import {FormsModule} from "@angular/forms";
import {NgIf} from "@angular/common";
import {IncompleteUser} from 'src/security/model/incomplete_user.model';
import {AuthService} from 'src/security/service/auth.service';
import {ErrorService} from 'src/core/services/error.service';
import {ActivatedRoute, Router} from '@angular/router';
import {ChangePassword} from 'src/security/model/change-password.model';
import {ToastrService} from 'src/core/services/toastr.service';

@Component({
  selector: 'app-reset-password',
    imports: [
        FeedbackTestComponent,
        FormsModule,
        NgIf,
    ],
  templateUrl: './reset-password.component.html',
  styleUrl: './reset-password.component.scss'
})
export class ResetPasswordComponent implements OnInit{

  composant = 'ResetPasswordComponent';
  showPassword = signal<boolean>(false);
  showNewPassword = signal(false);
  showConfirmPassword = signal(false);
  // entre 8 et 128 caractères, au moins 1 lettre et 1 chiffre
  passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,128}$/;
  passwordTouched = false;
  user: IncompleteUser | null = null;
  oldPassword = '';
  newPassword = '';
  confirmPassword = '';
  passwordError = '';
  confirmError = '';
  private route = inject(ActivatedRoute);
  context: 'change' | 'reset' = 'change';
  tokenResetPassword: string | null = null;

  constructor(
    private authService: AuthService,
    public errorService: ErrorService,
    private toastrService: ToastrService,
    public router: Router
  ) {}

  async ngOnInit(): Promise<void> {
    const contextParam = this.route.snapshot.queryParamMap.get('context') as 'change' | 'reset' | null;
    const token = this.route.snapshot.queryParamMap.get('token');

    if (token) {
      this.tokenResetPassword = token;
      try {
        await this.authService.verifyResetToken(token);
        this.context = 'reset';
      } catch (err) {
        this.errorService.showError("Une erreur s'est produite lors de votre réinitialisation de mot de passe. Veuillez réessayer.");
      }
    } else if (!contextParam) {
      this.errorService.showError("Une erreur s'est produite lors de votre réinitialisation de mot de passe. Veuillez réessayer.");
    }

    if (contextParam) {
      this.context = contextParam;
    }

    console.log(this.context);
  }


  onPasswordBlur(): void {
    this.passwordTouched = true;
    this.validatePassword();
  }

  validatePassword(): void {
    if (!this.newPassword) {
      this.passwordError = 'Le mot de passe est requis.';
    } else if (!this.passwordRegex.test(this.newPassword)) {
      this.passwordError = '🧠 8 caractères minimum, avec une lettre et un chiffre.';
    } else {
      this.passwordError = '';
    }
  }

  onPasswordInput(): void {
    if (!this.isPasswordValid(this.newPassword)) {
      this.passwordError = '🧠 8 caractères minimum, avec une lettre et un chiffre.';
    } else {
      this.passwordError = '';
    }

    this.validateConfirmation();
  }

  onConfirmPasswordInput(): void {
    this.validateConfirmation();
  }

  validateConfirmation(): void {
    if (this.newPassword && this.confirmPassword && this.newPassword !== this.confirmPassword) {
      this.confirmError = 'Les mots de passe ne correspondent pas.';
    } else {
      this.confirmError = '';
    }
  }

  isPasswordValid(password: string): boolean {
    const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,128}$/;
    return passwordRegex.test(password);
  }

  async submitPasswordChange(): Promise<void> {
    if (this.passwordError || this.confirmError) {
      this.errorService.showError('Corrigez les erreurs avant de valider.');
      return;
    }

    if (this.context === 'change') {
      const changePassword: ChangePassword = {
        oldPassword: this.oldPassword,
        newPassword: this.newPassword
      }
      try {
        await this.authService.submitPasswordChange(changePassword);
        this.toastrService.show({ message: 'Changement de mot de passe confirmé 👍', type: 'success' });
        void this.router.navigate(['profile']);
        return;
      } catch (err) {
        this.errorService.showError("Une erreur s'est produite lors de votre réinitialisation de mot de passe. Veuillez réessayer.")
      }
      return;
    }

    if (this.context === 'reset') {
      if (!this.tokenResetPassword) {
        this.errorService.showError("Une erreur est survenue, veuillez réessayer");
        return;
      }
      await this.authService.submitPasswordReset(this.tokenResetPassword, this.newPassword);
      return;
    }

    this.errorService.showError("Veuillez réessayer plus tard.");
  }

}
