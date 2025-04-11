import {AuthConfig} from 'angular-oauth2-oidc';
import {environment} from 'src/environments/environment';

export const authConfig: AuthConfig = {
  issuer: environment.issuer,
  redirectUri: window.location.origin,
  clientId: environment.googleClientId,
  scope: 'openid profile email',
  responseType: 'code',
  disablePKCE: false,
  showDebugInformation: true,
  strictDiscoveryDocumentValidation: false,

};
