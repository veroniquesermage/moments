import {inject, Injectable, signal} from '@angular/core';
import {Router} from '@angular/router';
import {environment} from 'src/environments/environment';
import {authConfig} from 'src/security/config/auth.config';
import {User} from 'src/security/model/user.model';
import {JwtResponse} from 'src/security/model/jwt-response.model';
import {firstValueFrom, Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {LoginRequest} from 'src/security/model/login-request.model';
import {ApiResponse} from 'src/core/models/api-response.model';
import {IncompleteUser} from 'src/security/model/incomplete_user.model';
import {RegisterRequest} from 'src/security/model/register-request.model';
import {ResetPasswordPayload} from 'src/security/model/reset-password-payload.model';
import {ChangePassword} from 'src/security/model/change-password.model';
import {GroupService} from 'src/core/services/group.service';

@Injectable({providedIn: 'root'})
export class AuthService {
  private router = inject(Router);

  // Signals centralisés
  profile = signal<User | null>(null);
  isLoggedIn = signal<boolean>(false);
  rememberMe = signal<boolean>(false);
  incompleteUser = signal<IncompleteUser | null>(null);

  private baseUrl = `${environment.backendBaseUrl}${environment.api.auth}`;

  constructor(private http: HttpClient,
              public groupService: GroupService) {
    this.handleGoogleCodeRedirect();
  }

  /**
   * Lance la redirection vers Google avec PKCE
   */
  async login(): Promise<void> {
    const state = Math.random().toString(36).substring(2);
    const codeVerifier = this.generateCodeVerifier();
    const codeChallenge = await this.generateCodeChallenge(codeVerifier);

    sessionStorage.setItem('pkce_code_verifier', codeVerifier);
    this.groupService.isLoading.set(true);
    window.location.href = `${environment.accountGoogle}` +
      `client_id=${authConfig.clientId}` +
      `&redirect_uri=${encodeURIComponent(authConfig.redirectUri!)}` +
      `&response_type=${authConfig.responseType}` +
      `&scope=${encodeURIComponent(authConfig.scope!)}` +
      `&state=${state}` +
      `&code_challenge=${codeChallenge}` +
      `&code_challenge_method=S256`;
  }

  /**
   * Gère le retour de Google avec ?code=...
   */
  private handleGoogleCodeRedirect(): void {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
      console.log('[OAuth2] Code reçu :', code);
      window.history.replaceState({}, document.title, window.location.pathname);
      this.sendCodeToBackend(code);
    }
  }

  /**
   * Appelle le backend pour échanger le code + verifier
   */
  private sendCodeToBackend(code: string): void {
    const codeVerifier = sessionStorage.getItem('pkce_code_verifier');
    const url = this.baseUrl + environment.api.google

    if (!codeVerifier) {
      console.error('[Auth] Code verifier manquant dans le sessionStorage');
      return;
    }
    this.groupService.isLoading.set(true);
    fetch(url, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code, codeVerifier, remember_me: this.rememberMe()}),
      credentials: 'include'
    })
      .then(res => res.json() as Promise<JwtResponse>)
      .then(async data => {
        console.log('[Backend] Réponse reçue :', data);
        if (data?.isNewUser && data?.profile) {
          this.incompleteUser.set({
            email: data.profile.email!,
            nom: data.profile.nom,
            prenom: data.profile.prenom
          })
          this.rememberMe.set(false);
          void this.router.navigate(['/auth/initialiser'], {
            queryParams: { context: 'google' }
          });
        } else if (data?.profile) {
          this.profile.set(data.profile);
          this.isLoggedIn.set(true);
        }
      })
      .catch(err => console.error('[Backend] Erreur :', err));
  }

  /**
   * Déconnecte l'utilisateur
   */
  async logout(): Promise<void> {

    for (const key in localStorage) {
      if (key.startsWith('app_kdo.')) {
        localStorage.removeItem(key);
      }
    }
    sessionStorage.removeItem('pkce_code_verifier');
    await firstValueFrom(this.logoutRefreshToken());
    this.profile.set(null);
    this.isLoggedIn.set(false);
    this.rememberMe.set(false);
    this.router.navigateByUrl('/');
  }

  /**
   * Génère un code_verifier (aléatoire base64)
   */
  private generateCodeVerifier(): string {
    const array = new Uint8Array(32);
    window.crypto.getRandomValues(array);
    return btoa(String.fromCharCode(...array))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  /**
   * Génère un code_challenge à partir du verifier
   */
  private async generateCodeChallenge(verifier: string): Promise<string> {
    const data = new TextEncoder().encode(verifier);
    const digest = await window.crypto.subtle.digest('SHA-256', data);
    return btoa(String.fromCharCode(...new Uint8Array(digest)))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  refreshToken(): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/refresh`, null);
  }

  logoutRefreshToken(): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/logout`, null);
  }

  async completeProfile(givenName: string, familyName: string | undefined): Promise<void> {
    const res = await fetch(`${this.baseUrl}/complete-profile`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      credentials: 'include',
      body: JSON.stringify({givenName, familyName})
    });
    if (!res.ok) {
      throw new Error("Échec de la mise à jour du profil");
    }
    const data: User = await res.json();
    this.incompleteUser.set(null);
    this.profile.set(data);
    this.isLoggedIn.set(true);
  }

  async registerWithCredentials(givenName: string, familyName: string | undefined, token: string | null) {
    const registerRequest: RegisterRequest = {
      token: token!,
      prenom: givenName,
      nom: familyName
    }

    await firstValueFrom(this.http.post<JwtResponse>(
      `${this.baseUrl}/register-credentials`,
      registerRequest,
      { withCredentials: true }
    ))
      .then(data => {
        console.log('[Backend] Réponse reçue :', data);
        if (data?.profile) {
          this.profile.set(data.profile);
          this.isLoggedIn.set(true);
        }
      })
      .catch(err => console.error('[Backend] Erreur :', err));
  }

  async checkMail(credentials: LoginRequest): Promise<ApiResponse<void>> {
    this.rememberMe.set(credentials.rememberMe);

    try {
      await firstValueFrom(this.http.post<void>(`${this.baseUrl}/check-email`, credentials));
      this.incompleteUser.set({
        email: credentials.email
      })
      return { success: true, data: undefined };
    } catch (error: any) {
      if (error.status === 409) {
        this.rememberMe.set(false);
        return { success: false, message: "❌ Ce mail est déjà utilisé avec un mot de passe." };
      }
      if (error.status === 423) {
        this.rememberMe.set(false);
        return { success: false, message: "❌ Ce mail est déjà lié à un compte Google." };
      }
      this.rememberMe.set(false);
      console.error('[AuthService] Erreur lors de la vérification du mail', error);
      return { success: false, message: "❌ Erreur inconnue lors de la vérification du mail." };
    }
  }

  async loginWithCredentials(email: string, password: string, rememberMe: boolean): Promise<JwtResponse> {
    const loginRequest: LoginRequest = { email, password, rememberMe };
    return await firstValueFrom(this.http.post<JwtResponse>(`${this.baseUrl}/credentials`, loginRequest));
  }

  async submitPasswordChange(changePassword: ChangePassword) {
    try {
      await firstValueFrom(
        this.http.patch<void>(
          `${this.baseUrl}/change-password`,
          changePassword,
          { withCredentials: true }
        )
      );
    } catch (err) {
      console.error('[Backend] Erreur :', err);
      throw err;
    }
  }

  async requestPasswordReset(mail: string){
    try {
      await firstValueFrom(
        this.http.post<string>(
          `${this.baseUrl}/request-password-reset`,
          {mail},
          { withCredentials: true }
        )
      );
      return true;
    } catch (err) {
      console.error('[Backend] Erreur :', err);
      throw err;
    }
  }

  async verifyResetToken(token: string): Promise<string> {
    try {
      const data = await firstValueFrom(
        this.http.post<string>(
          `${this.baseUrl}/verify-reset-token`,
          {token},
          { withCredentials: true }
        )
      );

      console.log('[Backend] Réponse reçue :', data);

      this.incompleteUser.set({ email: data });

      return data;
    } catch (err) {
      console.error('[Backend] Erreur :', err);
      throw err;
    }
  }

  async submitPasswordReset(token: string, newPassword: string) {
    const resetPasswordPayload: ResetPasswordPayload = {token, newPassword}

    await firstValueFrom(this.http.patch<JwtResponse>(
      `${this.baseUrl}/reset-password`,
      resetPasswordPayload,
      { withCredentials: true }
    ))
      .then(data => {
        console.log('[Backend] Réponse reçue :', data);
        if (data?.profile) {
          this.profile.set(data.profile);
          this.isLoggedIn.set(true);
        }
      })
      .catch(err => console.error('[Backend] Erreur :', err));
  }

  async switchToTiers(userTiersId: number) {
    const idEnc = encodeURIComponent(userTiersId);
    const url = `${this.baseUrl}/switch-to-tiers/${idEnc}`;
    try {
      const data = await firstValueFrom(this.http.post<JwtResponse>(url, {}, { withCredentials: true }));
      console.log('[Backend] Réponse reçue :', data);
      if (data?.profile) {
        this.profile.set(data.profile);
      }
    } catch (err) {
      console.error('[Backend] Erreur :', err);
      throw err;
    }
  }

  async switchToParent() {
    const url = `${this.baseUrl}/switch-to-parent`;
    try {
      const data = await firstValueFrom(this.http.post<JwtResponse>(url, {}, { withCredentials: true }));
      console.log('[Backend] Réponse reçue :', data);
      void await this.router.navigate(['/dashboard']);
      if (data?.profile) {
        this.profile.set(data.profile);
      }
    } catch (err) {
      console.error('[Backend] Erreur :', err);
      throw err;
    }
  }

}
