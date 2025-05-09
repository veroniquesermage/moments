import {GiftStatus} from 'src/core/enum/gift-status-.enum';

export interface GiftDTO {
  id?: number;
  nom: string;
  description?: string;
  url?: string;
  quantite: number;
  prix?: number;
  commentaire?: string;
  priorite: number;
  utilisateur: { id: number };
  statut: GiftStatus;
  reservePar?: { id: number };
  lieuLivraison?: string;
  dateLivraison?: string;
  recu: boolean;
}
