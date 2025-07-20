export interface User {
  id: number;
  email: string;
  prenom: string;
  nom?: string;
  googleId?: string;
  password?: string;
  dateCreation: string
}
