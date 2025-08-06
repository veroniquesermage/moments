import {User} from './user.model';

export interface JwtResponse {
  profile: User;
  isNewUser: boolean;
}
