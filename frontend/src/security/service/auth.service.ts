import {inject, Injectable, signal} from '@angular/core';
import {Router} from '@angular/router';
import {environment} from 'src/environments/environment';
import {authConfig} from 'src/security/config/auth.config';
import {User} from 'src/security/model/user.model';
import {JwtResponse} from 'src/security/model/jwt-response.model';
import {firstValueFrom, Observable} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {LoginRequest} from 'src/security/model/login-request.model';
import {RegisterRequest} from 'src/security/model/register-request.model';
import {CheckUserRequest} from 'src/security/model/check-user-request.model';
import {ApiResponse} from 'src/core/models/api-response.model';

@Injectable({providedIn: 'root'})
export class AuthService {
  private router = inject(Router);

  // Signals centralisés
  profile = signal<User | null>(null);
  isLoggedIn = signal<boolean>(false);
  rememberMe = signal<boolean>(false);

  private baseUrl = `${environment.backendBaseUrl}${environment.api.auth}`;

  constructor(private http: HttpClient) {
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

    fetch(url, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code, codeVerifier, remember_me: this.rememberMe()}),
      credentials: 'include'
    })
      .then(res => res.json() as Promise<JwtResponse>) // 👈 typage ici
      .then(data => {
        console.log('[Backend] Réponse reçue :', data);
        if (data?.profile) {
          this.profile.set(data.profile);
          this.isLoggedIn.set(true);
          this.rememberMe.set(false);
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

  async loginWithCredentials(credentials: LoginRequest): Promise<ApiResponse<void>> {
    const checkPayload: CheckUserRequest = {
      email: credentials.email,
      isGoogleLogin: false
    };

    try {
      await firstValueFrom(this.http.post<void>(`${this.baseUrl}/check-user`, checkPayload));
    } catch (err: any) {
      if (err.status === 404) {
        const params = new URLSearchParams({
          email: credentials.email,
          password: credentials.password,
          rememberMe: credentials.rememberMe ? 'true' : 'false'
        });
        await this.router.navigateByUrl(`/register?${params.toString()}`);
        return {success: true, data: undefined};
      }

      const message = err.status === 409
        ? '❌ Mauvais mode de connexion'
        : '❌ Erreur de vérification utilisateur';
      return {success: false, message};
    }

    try {
      const data = await firstValueFrom(
        this.http.post<JwtResponse>(`${this.baseUrl}/login`, credentials)
      );
      this.profile.set(data.profile);
      this.isLoggedIn.set(true);
      this.rememberMe.set(false);
      return {success: true, data: undefined};
    } catch (err) {
      return {success: false, message: '❌ Email ou mot de passe invalide'};
    }
  }

  async register(request: RegisterRequest): Promise<ApiResponse<void>> {
    try {
      const data = await firstValueFrom(
        this.http.post<JwtResponse>(`${this.baseUrl}/register`, request)
      );
      this.profile.set(data.profile);
      this.isLoggedIn.set(true);
      this.rememberMe.set(false);
      return {success: true, data: undefined};
    } catch (err) {
      return {success: false, message: '❌ Impossible de créer le compte'};
    }
  }
}
