import {GiftFollowed} from 'src/core/models/gift/gift-followed.model';

export interface GiftFollowedByAccount{
  accountLabel: string,
  total: number,
  gifts: GiftFollowed[]
}
