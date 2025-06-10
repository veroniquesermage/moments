import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftIdea} from 'src/core/models/gift/gift-ideas.model';

export interface GiftIdeasResponse{

  gift: GiftPublicResponse
  giftIdea: GiftIdea

}
