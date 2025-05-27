import {User} from 'src/security/model/user.model';

export interface GiftShared {
  id: number
  preneur: User
  cadeauId: number | undefined;
  participant: User
  montant: number
  rembourse: boolean
}
