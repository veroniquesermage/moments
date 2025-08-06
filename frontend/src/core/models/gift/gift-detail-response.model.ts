import {GiftShared} from 'src/core/models/gift/gift-shared.model';
import {RoleUser} from 'src/core/enum/role-user.enum';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftDelivery} from 'src/core/models/gift/gift-delivery.model';
import {GiftIdea} from 'src/core/models/gift/gift-ideas.model';
import {GiftPurchaseInfoSchema} from 'src/core/models/gift/gift-purchase-info.model';


export interface GiftDetailResponse {
  gift: GiftPublicResponse
  delivery?: GiftDelivery
  partage?: GiftShared[]
  ideas?: GiftIdea
  purchaseInfo?: GiftPurchaseInfoSchema
  estPartage: boolean
  droitsUtilisateur: RoleUser
}
