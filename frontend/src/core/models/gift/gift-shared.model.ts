import {UserDisplay} from 'src/core/models/user-display.model';

export interface GiftShared {
  id: number
  preneur: UserDisplay
  cadeauId: number | undefined;
  participant: UserDisplay
  montant: number
  rembourse: boolean
}
