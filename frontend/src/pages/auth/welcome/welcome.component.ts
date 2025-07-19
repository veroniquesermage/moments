import {Component, signal} from '@angular/core';
import {CommonModule, NgOptimizedImage} from '@angular/common';
import {AuthService} from 'src/security/service/auth.service';
import {LoadingComponent} from 'src/shared/components/loading/loading.component';
import {GroupService} from 'src/core/services/group.service';
import {FormsModule} from '@angular/forms';
import {LoginRequest} from 'src/security/model/login-request.model';
import {Router} from '@angular/router';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';
import {ModalActionType} from 'src/core/enum/modal-action.enum';

@Component({
  selector: 'app-welcome',
  standalone: true,
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.scss'],
  imports: [CommonModule, LoadingComponent, FormsModule, NgOptimizedImage, TerminalModalComponent],
})
export class WelcomeComponent {

  showPassword = signal<boolean>(false);
  email: string='';
  password: string='';
  stayLoggedIn: boolean = false;
  // entre 8 et 128 caractères, au moins 1 lettre et 1 chiffre
  passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,128}$/;
  emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
  passwordTouched = false;
  passwordError = '';
  emailTouched: boolean = false;
  emailError: string = '';
  showConfirmModal: boolean = false;
  message: string = '';
  modalActions: TerminalModalAction[] = [{ label: 'Mot de passe oublié', eventName: 'FORGOT', style: 'danger' },
    { label: 'Annuler', eventName: 'CANCEL', style: 'primary' }];

  constructor(
    public auth: AuthService,
    public groupeService: GroupService,
    public errorService: ErrorService,
    private router: Router) {
  }

  googleLogin() {
    this.auth.rememberMe.set(this.stayLoggedIn);
    void this.auth.login();
  }

  onPasswordInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.password = input.value;

    if (this.passwordTouched) {
      this.validatePassword();
    }
  }

  onPasswordBlur(): void {
    this.passwordTouched = true;
    this.validatePassword();
  }

  validatePassword(): void {
    if (!this.password) {
      this.passwordError = 'Le mot de passe est requis.';
    } else if (!this.passwordRegex.test(this.password)) {
      this.passwordError = '8 caractères minimum, avec une lettre et un chiffre.';
    } else {
      this.passwordError = '';
    }
  }

  onEmailInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    this.email = input.value;

    if (this.emailTouched) {
      this.validateEmail();
    }
  }

  onEmailBlur(): void {
    this.emailTouched = true;
    this.validateEmail();
  }

  validateEmail(): void {
    if (!this.email) {
      this.emailError = 'L’email est requis.';
    } else if (!this.emailRegex.test(this.email)) {
      this.emailError = 'Le format de l’email est incorrect.';
    } else {
      this.emailError = '';
    }
  }

  async loginWithCredentials() {
    try {
      const res = await this.auth.loginWithCredentials(this.email, this.password, this.stayLoggedIn);
      this.auth.profile.set(res.profile);
      this.auth.isLoggedIn.set(true);
    } catch (err: any) {
      console.error('[Login] Erreur backend', err);

      switch (err.status) {
        case 401:
          this.showConfirmModal = true;
          break;
        case 403:
          this.errorService.showError('Votre compte est temporairement bloqué.');
          break;
        case 404:
          this.errorService.showError('Aucun compte n’existe pour cette adresse.');
          break;
        default:
          this.errorService.showError('Veuillez réessayer plus tard.');
      }
    }
  }

  async registerWithCredentials() {
    const credentials: LoginRequest = {
      email: this.email,
      password: this.password,
      rememberMe: this.stayLoggedIn
    };
    const result = await this.auth.checkMail(credentials);
    if (!result.success) {
      this.errorService.showError(result.message);
    }
  }

  async handleClicked(eventName: string) {
    if (eventName === ModalActionType.FORGOT) {
      await this.auth.requestPasswordReset(this.email);
      this.showConfirmModal = false;
    } else if (eventName === ModalActionType.CANCEL) {
      this.showConfirmModal = false;
    }
  }

  preventIfInvalid(event: KeyboardEvent): void {
    const activeElement = document.activeElement as HTMLElement;

    const isInputField = activeElement?.tagName === 'INPUT' || activeElement?.tagName === 'TEXTAREA';

    if (isInputField && (this.emailError || this.passwordError)) {
      event.preventDefault(); // on empêche juste le submit implicite
    }
  }

}

