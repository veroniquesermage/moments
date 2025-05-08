import {GiftStatus} from 'src/core/enum/gift-status-.enum';

export interface Gift {
  id?: number;
  nom: string;
  description?: string;
  url?: string;
  quantite: number;
  prix?: number;
  commentaire?: string;
  priorite: number;
  utilisateurId: number;
  statut: GiftStatus;
  reserveParId?: number;
  lieuLivraison?: string;
  dateLivraison?: string; // format ISO (string)
  recu: boolean;
}
