import {bootstrapApplication} from '@angular/platform-browser';
import {AppComponent} from './app/app.component';
import {OAuthModule} from 'angular-oauth2-oidc';
import {importProvidersFrom, LOCALE_ID} from '@angular/core';
import {provideHttpClient} from '@angular/common/http';
import {provideRouter} from '@angular/router';
import {routes} from 'src/app/app.routes';
import { registerLocaleData } from '@angular/common';
import localeFr from '@angular/common/locales/fr';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import {provideToastr} from 'ngx-toastr';

registerLocaleData(localeFr);

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    importProvidersFrom(OAuthModule.forRoot(), BrowserAnimationsModule),
    provideToastr({
      positionClass: 'toast-bottom-right',
    }),
    { provide: LOCALE_ID, useValue: 'fr-FR' }
  ]
});
