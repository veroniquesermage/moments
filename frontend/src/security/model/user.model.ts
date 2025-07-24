export interface User {
  id: number;
  email?: string;
  prenom: string;
  nom?: string;
  dateCreation: string;
  isCompteTiers: boolean
  hasPassword: boolean
}
