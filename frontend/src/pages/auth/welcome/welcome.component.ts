import {Component, signal} from '@angular/core';
import {CommonModule, NgOptimizedImage} from '@angular/common';
import {AuthService} from 'src/security/service/auth.service';
import {LoadingComponent} from 'src/shared/components/loading/loading.component';
import {GroupService} from 'src/core/services/group.service';
import {FormsModule} from '@angular/forms';
import {LoginRequest} from 'src/security/model/login-request.model';
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
    public errorService: ErrorService) {
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
          this.message = '<strong>Ce n\'est pas le bon mot de passe !</strong><br>' +
            'Vous pouvez réessayer (avec le bon, cette fois 😏) ou réinitialiser votre mot de passe.<br>' +
            'Attention : vous n\'avez droit qu\'à <strong>5 tentatives</strong> !'
          this.showConfirmModal = true;
          break;
        case 403:
          this.errorService.showError('<strong>Oups, compte temporairement bloqué !</strong><br>' +
            'On vous avait prévenu : 5 tentatives seulement...<br>' +
            'Prenez une pause de 15 minutes et réinitialisez-le !');
          break;
        case 404:
          this.errorService.showError('<strong>Hmm... cette adresse ne nous dit rien !</strong><br>\n' +
            'Aucun compte n\'existe pour cet email.<br>' +
            'Et si c\'était le moment d\'en créer un ?');
          break;
        case 409:
          this.errorService.showError('<strong>Ce compte existe bien, mais pas de mot de passe ici !</strong><br>' +
            'Il est timide… il ne parle que Google. Cliquez sur le bouton juste au-dessus.');
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
    if (result.success) {
      this.modalActions = [{ label: 'OK', eventName: 'CANCEL', style: 'primary' }];
      this.message = '<strong>Un email vient de partir !</strong> <br> Vous avez 30min pour cliquer sur le lien et terminer votre inscription.';
      this.showConfirmModal = true;
    } else {
      this.errorService.showError(result.message);
    }
  }

  async handleClicked(eventName: string) {
    if (eventName === ModalActionType.FORGOT) {
      const response = await this.auth.requestPasswordReset(this.email);
      if (response){
        this.modalActions = [
          { label: 'OK', eventName: 'CANCEL', style: 'primary' }];
        this.message = '<strong>Un email vient de partir !</strong> <br> Cliquez sur le lien qu’il contient pour réinitialiser votre mot de passe.';
      } else {
        this.showConfirmModal = false;
        this.errorService.showError('Oups! Un problème est survenu. <br> Veuillez réessayer plus tard');
      }

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

  asKeyboardEvent(event: Event): KeyboardEvent {
    return event as KeyboardEvent;
  }

}

