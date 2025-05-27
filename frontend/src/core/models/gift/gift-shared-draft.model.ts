import {User} from 'src/security/model/user.model';

export interface GiftSharedDraft {
  participant: User | null;
  montant: number | null;
}
