import {GiftDTO} from 'src/core/models/gift-dto.model';
import {Gift} from 'src/core/models/gift.model';

export class GiftMapper {
  static fromDTO(dto: GiftDTO): Gift {
    return {
      id: dto.id,
      nom: dto.nom,
      description: dto.description,
      url: dto.url,
      quantite: dto.quantite,
      prix: dto.prix,
      commentaire: dto.commentaire,
      priorite: dto.priorite,
      utilisateurId: dto.utilisateur.id,
      statut: dto.statut,
      reserveParId: dto.reservePar?.id,
      lieuLivraison: dto.lieuLivraison,
      dateLivraison: dto.dateLivraison,
      recu: dto.recu
    };
  }

  static toDTO(gift: Gift): GiftDTO {
    return {
      id: gift.id,
      nom: gift.nom,
      description: gift.description,
      url: gift.url,
      quantite: gift.quantite,
      prix: gift.prix,
      commentaire: gift.commentaire,
      priorite: gift.priorite,
      statut: gift.statut,
      lieuLivraison: gift.lieuLivraison,
      dateLivraison: gift.dateLivraison,
      recu: gift.recu,

      // Champs imbriqués → attention à reconstruire la bonne forme attendue côté backend
      utilisateur: { id: gift.utilisateurId },
      reservePar: gift.reserveParId ? { id: gift.reserveParId } : undefined
    };
  }

}
