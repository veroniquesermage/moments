import {UserTiersResponse} from 'src/core/models/user-tiers-response.model';

export interface GiftPurchaseInfoSchema {
  giftId: number
  prixReel?: number
  commentaire?: string
  compteTiers?: UserTiersResponse

}

