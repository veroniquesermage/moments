import {Gift} from 'src/core/models/gift/gift.model';
import {GiftShared} from 'src/core/models/gift/gift_shared.model';
import {RoleUser} from 'src/core/enum/role-user.enum';


export interface GiftDetailResponse {
  gift: Gift
  partage?: GiftShared
  est_partage: boolean
  droits_utilisateur: RoleUser
}
