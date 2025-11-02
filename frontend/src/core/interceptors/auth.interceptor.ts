import {Injectable} from '@angular/core';
import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {catchError, Observable, switchMap, throwError, BehaviorSubject, filter, take} from 'rxjs';
import {Router} from '@angular/router';
import {AuthService} from 'src/security/service/auth.service';
import {TokenService} from 'src/security/service/token.service';
import {GroupContextService} from 'src/core/services/group-context.service';

@Injectable({ providedIn: 'root' })
export class AuthInterceptor implements HttpInterceptor {
  private isRefreshing = false;
  private refreshTokenSubject: BehaviorSubject<boolean> = new BehaviorSubject<boolean>(false);
  private refreshAttempts = 0;
  private readonly MAX_REFRESH_ATTEMPTS = 1;

  constructor(
    private tokenService: TokenService,
    private authService: AuthService,
    private router: Router,
    private groupContextService: GroupContextService
  ) {
  }

  intercept(
    req: HttpRequest<unknown>,
    next: HttpHandler
  ): Observable<HttpEvent<unknown>> {

    const ignoredAuthRoutes = [
      '/auth/credentials',
      '/auth/google',
      '/auth/register-credentials',
      '/auth/logout',
      '/auth/refresh',  // ← CRITIQUE : évite la boucle infinie !
      '/auth/request-password-reset',
      '/auth/verify-reset-token',
      '/auth/check-email',
      '/auth/reset-password',
    ];

    if (ignoredAuthRoutes.some(url => req.url.includes(url))) {
      const groupId = this.groupContextService.getGroupId();
      const authReq = req.clone({
        withCredentials: true,
        setHeaders: groupId
          ? {'X-Group-Id': groupId.toString()}
          : {}
      });
      return next.handle(authReq);
    }

    const groupId = this.groupContextService.getGroupId();

    // Cloner la requête pour ajouter le X-Group-Id et withCredentials
    const authReq = req.clone({
      withCredentials: true,
      setHeaders: groupId
        ? {'X-Group-Id': groupId.toString()}
        : {}
    });

    return next.handle(authReq).pipe(
      catchError(err => {
        if (err.status === 401) {
          return this.handle401Error(authReq, next);
        }
        // pas de 401 → on ré-émet l'erreur
        return throwError(() => err);
      })
    );
  }

  private handle401Error(req: HttpRequest<unknown>, next: HttpHandler): Observable<HttpEvent<unknown>> {
    // PROTECTION 1 : Race condition - Si un refresh est déjà en cours, attendre qu'il se termine
    if (this.isRefreshing) {
      return this.refreshTokenSubject.pipe(
        filter(success => success === true),
        take(1),
        switchMap(() => next.handle(req)),
        catchError(err => {
          // Si même après le refresh ça échoue, logout
          this.logout();
          return throwError(() => err);
        })
      );
    }

    // PROTECTION 2 : Limite de tentatives pour éviter la boucle infinie
    if (this.refreshAttempts >= this.MAX_REFRESH_ATTEMPTS) {
      console.warn('[AuthInterceptor] Max refresh attempts reached, forcing logout');
      this.logout();
      return throwError(() => new Error('Max refresh attempts reached'));
    }

    // Lancer le refresh
    this.isRefreshing = true;
    this.refreshAttempts++;
    this.refreshTokenSubject.next(false);

    return this.authService.refreshToken().pipe(
      switchMap(() => {
        // Refresh réussi - reset des compteurs
        this.isRefreshing = false;
        this.refreshAttempts = 0;  // ← IMPORTANT : reset on success
        this.refreshTokenSubject.next(true);

        return next.handle(req);
      }),
      catchError(refreshErr => {
        // Refresh échoué définitivement
        console.error('[AuthInterceptor] Refresh failed:', refreshErr);
        this.isRefreshing = false;
        this.refreshTokenSubject.next(false);
        this.logout();
        return throwError(() => refreshErr);
      })
    );
  }

  private logout(): void {
    this.refreshAttempts = 0;
    this.tokenService.clear();
    void this.authService.logout();
  }
}
