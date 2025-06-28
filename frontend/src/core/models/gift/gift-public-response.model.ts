import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {UserDisplay} from 'src/core/models/user-display.model';

export interface GiftPublicResponse {
  id?: number;
  destinataire: UserDisplay;
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
  reservePar?: UserDisplay;
  dateReservation?: string;
  expirationReservation?: string;
}
