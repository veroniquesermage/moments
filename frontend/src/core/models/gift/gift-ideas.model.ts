import {User} from 'src/security/model/user.model';

export interface GiftIdea {
  id: number
  cree_par: User
  visibilite: boolean
}
