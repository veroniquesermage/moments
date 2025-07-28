import {bootstrapApplication} from '@angular/platform-browser';
import {AppComponent} from './app/app.component';
import {OAuthModule} from 'angular-oauth2-oidc';
import {importProvidersFrom, inject, LOCALE_ID, provideAppInitializer} from '@angular/core';
import {HTTP_INTERCEPTORS, provideHttpClient, withInterceptorsFromDi} from '@angular/common/http';
import {provideRouter} from '@angular/router';
import {routes} from 'src/app/app.routes';
import {registerLocaleData} from '@angular/common';
import localeFr from '@angular/common/locales/fr';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {StartupService} from 'src/core/services/startup.service';
import {AuthInterceptor} from 'src/core/interceptors/auth.interceptor';

registerLocaleData(localeFr);

bootstrapApplication(AppComponent, {
  providers: [
    { provide: LOCALE_ID, useValue: 'fr-FR' },
    provideRouter(routes),
    provideHttpClient(
      withInterceptorsFromDi()
    ),
    { provide: HTTP_INTERCEPTORS, useClass: AuthInterceptor, multi: true },
    importProvidersFrom(OAuthModule.forRoot(), BrowserAnimationsModule),
    provideAppInitializer(async () => {
      const startup = inject(StartupService);
      await startup.handleAppStartup();
    })
  ]
});

