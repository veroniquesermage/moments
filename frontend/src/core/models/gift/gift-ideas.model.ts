import {User} from 'src/security/model/user.model';

export interface GiftIdea {
  id: number
  proposee_par: User
  visibilite: boolean
}
