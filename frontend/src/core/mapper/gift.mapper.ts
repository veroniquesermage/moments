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
}
