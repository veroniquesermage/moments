import {inject, Injectable, signal} from '@angular/core';
import {Router} from '@angular/router';
import {environment} from 'src/environments/environment';
import {authConfig} from 'src/security/config/auth.config';
import {User} from 'src/security/model/user.model';
import {JwtResponse} from 'src/security/model/jwt-response.model'; // DTO miroir backend

@Injectable({providedIn: 'root'})
export class AuthService {
  private router = inject(Router);

  // Signals centralisés
  profile = signal<User | null>(null);
  isLoggedIn = signal<boolean>(false);

  constructor() {
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

    fetch(`${environment.backendBaseUrl}${environment.api.auth}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({code, codeVerifier})
    })
      .then(res => res.json() as Promise<JwtResponse>) // 👈 typage ici
      .then(data => {
        console.log('[Backend] Réponse reçue :', data);
        if (data?.token) {
          localStorage.setItem('app_kdo.jwt', data.token);
          this.profile.set(data.profile);
          this.isLoggedIn.set(true);
        }
      })
      .catch(err => console.error('[Backend] Erreur :', err));
  }

  /**
   * Déconnecte l'utilisateur
   */
  logout(): void {
    for (const key in localStorage) {
      if (key.startsWith('app_kdo.')) {
        localStorage.removeItem(key);
      }
    }
    sessionStorage.removeItem('pkce_code_verifier');
    this.profile.set(null);
    this.isLoggedIn.set(false);
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
}
