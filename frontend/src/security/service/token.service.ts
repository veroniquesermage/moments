import {Injectable} from '@angular/core';
import {jwtDecode} from 'jwt-decode';
import {AccessTokenPayload} from 'src/security/model/access-token-payload.model';

@Injectable({
  providedIn: 'root'
})
export class TokenService {

  getAccessToken(): string | null {
    const match = document.cookie.match(/(?:^|; )access_token=([^;]*)/);
    return match ? decodeURIComponent(match[1]) : null;
  }

  decodeAccessToken(): AccessTokenPayload | null {
    const token = this.getAccessToken();
    if (!token) return null;

    try {
      return jwtDecode<AccessTokenPayload>(token);
    } catch (err) {
      console.warn('Token invalide :', err);
      return null;
    }
  }

  isTokenExpired(): boolean {
    const SAFETY_MARGIN = 10_000; // 10 s
    const payload = this.decodeAccessToken();
    if (!payload) return true;

    return payload.exp * 1000 < (Date.now() + SAFETY_MARGIN);
  }

  hasRememberMe(): boolean {
    const payload = this.decodeAccessToken();
    return payload?.remember_me ?? false;
  }

  clear(): void {
    // Supprime les cookies gérés côté frontend
    this.deleteAccessToken();

    localStorage.removeItem('app_kdo.activeGroupId');
  }

  deleteAccessToken(): void {
    document.cookie = 'access_token=; Max-Age=0; path=/';
  }

}
