import {Injectable} from '@angular/core';
import {HttpEvent, HttpHandler, HttpInterceptor, HttpRequest} from '@angular/common/http';
import {catchError, Observable, switchMap, throwError} from 'rxjs';
import {Router} from '@angular/router';
import {AuthService} from 'src/security/service/auth.service';
import {TokenService} from 'src/security/service/token.service';
import {GroupContextService} from 'src/core/services/group-context.service';

@Injectable({ providedIn: 'root' })
export class AuthInterceptor implements HttpInterceptor {
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
          // 1) appeler refreshToken() pour que le serveur mette à jour le cookie
          return this.authService.refreshToken().pipe(
            // 2) une fois terminé, on clone et rejoue la requête originale
            switchMap(() => {
              const retryReq = authReq.clone();
              return next.handle(retryReq);
            }),
            // 3) si le refresh échoue, on logout
            catchError(innerErr => {
              this.tokenService.clear();
              void this.router.navigate(['/']);
              return throwError(() => innerErr);
            })
          );
        }
        // pas de 401 ou pas de remember-me → on ré-émet l’erreur
        return throwError(() => err);
      })
    );
  }
}
