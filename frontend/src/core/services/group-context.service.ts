import {Injectable} from '@angular/core';
import {User} from 'src/security/model/user.model';

@Injectable({ providedIn: 'root' })
export class GroupContextService{

  memberCache: User[] | undefined = undefined;

  setGroupId(id: number){
    localStorage.setItem('activeGroupId', id.toString());
  }

  getGroupId(): number | null {
    const id = localStorage.getItem('activeGroupId');
    return id ? Number(id) : null;
  }


}
