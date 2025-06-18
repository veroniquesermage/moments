import {UserDisplay} from 'src/core/models/user-display.model';

export interface GiftSharedDraft {
  participant: UserDisplay | null;
  montant: number | null;
}
