import {GiftDTO} from 'src/core/models/gift/gift-dto.model';
import {Gift} from 'src/core/models/gift/gift.model';


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
      utilisateur: dto.utilisateur,
      statut: dto.statut,
      reservePar: dto.reservePar,
      dateReservation: dto.dateReservation,
      lieuLivraison: dto.lieuLivraison,
      dateLivraison: dto.dateLivraison,
      recu: dto.recu,
      marque: dto.marque,
      magasin: dto.magasin,
      prixReel: dto.prixReel,
      fraisPort: dto.fraisPort
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
      dateReservation: gift.dateReservation,
      marque: gift.marque,
      magasin: gift.magasin,
      prixReel: gift.prixReel,
      fraisPort: gift.fraisPort,

      // Champs imbriqués → attention à reconstruire la bonne forme attendue côté backend
      utilisateur: gift.utilisateur,
      reservePar: gift.reservePar || undefined
    };
  }

}
