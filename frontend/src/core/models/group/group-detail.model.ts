import {User} from 'src/security/model/user.model';
import {GroupResume} from 'src/core/models/group/group-resume.model';

export interface GroupDetail {
  groupe: GroupResume,
  admins: User[],
  surnom?: string,
  role: string,
  prenom: string
}
