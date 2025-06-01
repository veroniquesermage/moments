import {GiftStatus} from 'src/core/enum/gift-status.enum';

export interface GiftCreate{

  destinataireId: number;
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
  statut: GiftStatus.DISPONIBLE;
}
