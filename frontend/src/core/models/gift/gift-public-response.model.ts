import {User} from 'src/security/model/user.model';
import {GiftStatus} from 'src/core/enum/gift-status.enum';

export interface GiftPublicResponse {
  id?: number;
  destinataire: User;
  nom: string;
  description?: string;
  marque?: string;
  magasin?: string;
  url?: string;
  quantite: number;
  prix?: number;
  fraisPort?: number;
  commentaire?: string;
  priorite: number;

  statut: GiftStatus;
  reservePar?: User;
  dateReservation?: string;
}
