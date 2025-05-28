import {bootstrapApplication} from '@angular/platform-browser';
import {AppComponent} from './app/app.component';
import {OAuthModule} from 'angular-oauth2-oidc';
import {importProvidersFrom} from '@angular/core';
import {provideHttpClient} from '@angular/common/http';
import {provideRouter} from '@angular/router';
import {routes} from 'src/app/app.routes';
import './styles/retro-terminal.css';
import { registerLocaleData } from '@angular/common';
import localeFr from '@angular/common/locales/fr';

registerLocaleData(localeFr);

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes),
    provideHttpClient(),
    importProvidersFrom(OAuthModule.forRoot())
  ]
});
