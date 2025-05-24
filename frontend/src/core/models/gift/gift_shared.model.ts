import {User} from 'src/security/model/user.model';

export interface GiftShared {
  id: number
  preneur: User
  cadeau_id: number
  participant: User
  montant: number
  rembourse: boolean
}
