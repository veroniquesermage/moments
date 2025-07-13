import {Component, signal} from '@angular/core';
import {CommonModule, NgOptimizedImage} from '@angular/common';
import {AuthService} from 'src/security/service/auth.service';
import {LoadingComponent} from 'src/shared/components/loading/loading.component';
import {GroupService} from 'src/core/services/group.service';
import {FormsModule} from '@angular/forms';
import {LoginRequest} from 'src/security/model/login-request.model';

@Component({
  selector: 'app-welcome',
  standalone: true,
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.scss'],
  imports: [CommonModule, LoadingComponent, FormsModule, NgOptimizedImage],
})
export class WelcomeComponent {

  showPassword = signal<boolean>(false);
  email: string='';
  password: string='';
  stayLoggedIn: boolean = false;
  // entre 8 et 128 caractères, au moins 1 lettre et 1 chiffre
  passwordRegex = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,128}$/;
  passwordTouched = false;
  passwordError = '';


  constructor(public auth: AuthService, public groupeService: GroupService) {
  }

  submitEmailPassword(): void {
    this.auth.rememberMe.set(this.stayLoggedIn);
    const credentials: LoginRequest = {
      email: this.email ?? '',
      password: this.password ?? '',
      rememberMe: this.stayLoggedIn
    };

    this.auth.loginWithCredentials(credentials);
  }


  onPasswordInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    const value = input.value;

    this.passwordTouched = true;
    this.password = value;

    if (!this.isPasswordValid(value)) {
      this.passwordError = '8 caractères minimum, dont au moins une lettre et un chiffre.';
    } else {
      this.passwordError = '';
    }
  }

  isPasswordValid(password: string): boolean {
    return this.passwordRegex.test(password);
  }

  googleLogin() {
    this.auth.rememberMe.set(this.stayLoggedIn);
    this.auth.login();
  }
}

