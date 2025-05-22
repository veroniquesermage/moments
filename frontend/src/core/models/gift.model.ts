import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {User} from 'src/security/model/user.model';

export interface Gift {
  id?: number;
  nom: string;
  description?: string;
  url?: string;
  quantite: number;
  prix?: number;
  commentaire?: string;
  priorite: number;
  utilisateur: User;
  statut: GiftStatus;
  reservePar?: User;
  dateReservation?: string;
  lieuLivraison?: string;
  dateLivraison?: string; // format ISO (string)
  recu: boolean;
  marque: string;
  magasin: string;
  prixReel: number;
  fraisPort: number;
}
