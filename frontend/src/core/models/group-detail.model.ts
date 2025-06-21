import {GroupResume} from 'src/core/models/group-resume.model';
import {User} from 'src/security/model/user.model';

export interface GroupDetail {
  groupe: GroupResume,
  admins: User[],
  surnom?: string,
  role: string,
  prenom: string
}
