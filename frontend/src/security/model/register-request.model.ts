export interface RegisterRequest {
  prenom: string;
  nom: string;
  email?: string;
  password?: string;
  googleId?: string;
  rememberMe: boolean;
}
