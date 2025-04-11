import {inject, Injectable, signal} from '@angular/core';
import {Router} from '@angular/router';
import {environment} from 'src/environments/environment';
import {authConfig} from 'src/security/config/auth.config';


@Injectable({providedIn: 'root'})
export class AuthService {
  private router = inject(Router);
  profile = signal<any>(null);
  isLoggedIn = signal<boolean>(false);
  identityClaims = signal<any>(null);

  constructor() {
    this.handleGoogleCodeRedirect();
  }

  async login(): Promise<void> {

    const state = Math.random().toString(36).substring(2);
    const codeVerifier = this.generateCodeVerifier();
    const codeChallenge = await this.generateCodeChallenge(codeVerifier);

    sessionStorage.setItem('pkce_code_verifier', codeVerifier);

    window.location.href = environment.accountGoogle +
      `client_id=${authConfig.clientId!}` +
      `&redirect_uri=${encodeURIComponent(authConfig.redirectUri!)}` +
      `&response_type=${authConfig.responseType!}` +
      `&scope=${encodeURIComponent(authConfig.scope!)}` +
      `&state=${state}` +
      `&code_challenge=${codeChallenge}` +
      `&code_challenge_method=S256`;
  }

  logout(): void {
    localStorage.removeItem('jwt');
    this.profile.set(null);
    this.isLoggedIn.set(false);
    this.identityClaims.set(null);
    this.router.navigateByUrl('/');
  }

  private handleGoogleCodeRedirect(): void {
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
      console.log('[OAuth2] Code reçu :', code);

      window.history.replaceState({}, document.title, window.location.pathname);

      this.sendCodeToBackend(code);
    }
  }

  private sendCodeToBackend(code: string): void {
    fetch(environment.backendUrl + environment.backendAuth, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({code})
    })
      .then(res => res.json())
      .then(data => {
        console.log('[Backend] Réponse reçue :', data);
        if (data && data.token) {
          localStorage.setItem('jwt', data.token);
          this.profile.set(data.profile || {});
          this.identityClaims.set(data.profile || {});
          this.isLoggedIn.set(true);
        }
      })
      .catch(err => console.error('[Backend] Erreur:', err));
  }

  private generateCodeVerifier(): string {
    const array = new Uint8Array(32);
    window.crypto.getRandomValues(array);
    return btoa(String.fromCharCode(...array))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }

  private async generateCodeChallenge(verifier: string): Promise<string> {
    const data = new TextEncoder().encode(verifier);
    const digest = await window.crypto.subtle.digest('SHA-256', data);
    return btoa(String.fromCharCode(...new Uint8Array(digest)))
      .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
  }
}

