import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftDelivery} from 'src/core/models/gift/gift-delivery.model';
import {GiftShared} from 'src/core/models/gift/gift-shared.model';

export interface GiftFollowed{
  gift: GiftPublicResponse,
  delivery?: GiftDelivery,
  partage?: GiftShared
}
