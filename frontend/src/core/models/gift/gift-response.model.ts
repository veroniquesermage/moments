import {User} from 'src/security/model/user.model';

export interface GiftResponse {
  id?: number;
  destinataire: User;
  nom: string;
  description?: string;
  marque: string;
  magasin: string;
  url?: string;
  quantite: number;
  prix?: number;
  fraisPort: number;
  commentaire?: string;
  priorite: number;
}
