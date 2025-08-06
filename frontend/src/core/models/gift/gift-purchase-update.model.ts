import {UserDisplay} from 'src/core/models/user-display.model';

export interface GiftPurchaseUpdate {
  giftId: number
  prixReel?: number
  commentaire?: string
  compteTiers?: UserDisplay
}

