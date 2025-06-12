export interface User {
  id: number;
  email: string;
  name: string;
  googleId?: string; // facultatif, si jamais tu l’exposes
  dateCreation: string
}
