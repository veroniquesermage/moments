import {bootstrapApplication} from '@angular/platform-browser';
import {AppComponent} from './app/app.component';
import {OAuthModule} from 'angular-oauth2-oidc';
import {importProvidersFrom} from '@angular/core';
import {provideHttpClient} from '@angular/common/http';

bootstrapApplication(AppComponent, {
  providers: [
    provideHttpClient(),
    importProvidersFrom(OAuthModule.forRoot())
  ]
});
