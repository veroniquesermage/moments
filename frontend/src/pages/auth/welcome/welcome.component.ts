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
      this.passwordError = 'Un mot de passe serait fort apprécié.';
    } else if (!this.passwordRegex.test(this.password)) {
      this.passwordError = 'Huit caractères au minimum, agrémentés d\'une lettre et d\'un chiffre.';
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
      this.emailError = 'Votre adresse électronique nous fait défaut.';
    } else if (!this.emailRegex.test(this.email)) {
      this.emailError = 'Cette adresse manque singulièrement de correction.';
    } else {
      this.emailError = '';
    }
  }

  async loginWithCredentials() {
    // Valider les champs avant d'envoyer la requête
    this.emailTouched = true;
    this.passwordTouched = true;
    this.validateEmail();
    this.validatePassword();

    // Si des erreurs de validation existent, ne pas continuer
    if (this.emailError || this.passwordError) {
      return;
    }

    try {
      const res = await this.auth.loginWithCredentials(this.email, this.password, this.stayLoggedIn);
      this.auth.profile.set(res.profile);
      this.auth.isLoggedIn.set(true);
    } catch (err: any) {
      console.error('[Login] Erreur backend', err);

      switch (err.status) {
        case 401:
          this.message = '<strong>Ce mot de passe ne saurait convenir !</strong><br>' +
            'Vous pouvez tenter de nouveau (avec le bon, cette fois) ou procéder à sa réinitialisation.<br>' +
            'Gardez à l\'esprit que vous ne disposez que de <strong>5 tentatives</strong> — nous ne sommes pas des sauvages, mais tout de même.'
          this.showConfirmModal = true;
          break;
        case 403:
          this.errorService.showError('<strong>Compte temporairement suspendu !</strong><br>' +
            'Nous vous avions pourtant avertis : cinq tentatives tout au plus...<br>' +
            'Accordez-vous une pause de quinze minutes et procédez à sa réinitialisation.');
          break;
        case 404:
          this.errorService.showError('<strong>Cette adresse nous est parfaitement inconnue !</strong><br>\n' +
            'Aucun compte ne correspond à cette adresse électronique.<br>' +
            'Ne serait-ce point l\'occasion d\'en établir un ?');
          break;
        case 409:
          this.errorService.showError('<strong>Ce compte existe bel et bien, mais point de mot de passe !</strong><br>' +
            'Il cultive une certaine réserve... il ne converse qu\'avec Google. Cliquez donc sur le bouton ci-dessus.');
          break;
        default:
          this.errorService.showError('Un contretemps inopiné s\'est produit. Veuillez tenter de nouveau sous peu.');
      }
    }
  }

  async registerWithCredentials() {
    // Valider les champs avant d'envoyer la requête
    this.emailTouched = true;
    this.passwordTouched = true;
    this.validateEmail();
    this.validatePassword();

    // Si des erreurs de validation existent, ne pas continuer
    if (this.emailError || this.passwordError) {
      return;
    }

    const credentials: LoginRequest = {
      email: this.email,
      password: this.password,
      rememberMe: this.stayLoggedIn
    };
    const result = await this.auth.checkMail(credentials);
    if (result.success) {
      this.modalActions = [{ label: 'OK', eventName: 'CANCEL', style: 'primary' }];
      this.message = '<strong>Un courrier électronique vient de vous être expédié !</strong> <br> Vous disposez de trente minutes pour cliquer sur le lien et parachever votre inscription.';
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
        this.message = '<strong>Un courrier électronique vient de vous être expédié !</strong> <br> Cliquez sur le lien qu\'il contient pour réinitialiser votre mot de passe.';
      } else {
        this.showConfirmModal = false;
        this.errorService.showError('Un fâcheux contretemps s\'est produit. <br> Veuillez tenter de nouveau sous peu.');
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

