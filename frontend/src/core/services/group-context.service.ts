import {Injectable} from '@angular/core';
import {User} from 'src/security/model/user.model';
import {UserGroupService} from 'src/core/services/user-group.service';
import {Router} from '@angular/router';

@Injectable({ providedIn: 'root' })
export class GroupContextService{

  memberCache: User[] | undefined = undefined;
  constructor(private userGroupService: UserGroupService,
              private router: Router) {
  }

  async setGroupContext(id: number): Promise<void> {
    const groupUsers = await this.userGroupService.fetchUserGroup(id);
    if (groupUsers.success) {
      this.memberCache = groupUsers.data;
    } else {
      this.memberCache = [];
      console.warn('[GroupContext] Échec du fetch des membres pour le groupe', id);
    }

    const safeId = Number(id);
    localStorage.setItem('app_kdo.activeGroupId', safeId.toString());
    localStorage.setItem('app_kdo.groupMembers', JSON.stringify(this.memberCache));
    localStorage.setItem('app_kdo.groupMembers_timestamp', Date.now().toString());
  }


  getGroupId(): number {
    const id = localStorage.getItem('activeGroupId');
    if (!id || isNaN(Number(id))) {
      this.router.navigate(['/onboarding']);
    }
    return Number(id);
  }

  async getGroupMembers(): Promise<User[]> {
    if (this.memberCache && !this.isMembersCacheTooOld()) {
      return await Promise.resolve(this.memberCache);
    }

    const raw = localStorage.getItem('groupMembers');
    if (raw && !this.isMembersCacheTooOld()) {
      this.memberCache = JSON.parse(raw);
      return await Promise.resolve(this.memberCache!);
    }
    return await this.refreshMembers();
  }

  private isMembersCacheTooOld(): boolean {
    const ts = localStorage.getItem('groupMembers_timestamp');
    if (!ts) return true;

    const age = Date.now() - Number(ts);
    const maxAge = 1000 * 60 * 60 * 24;
    return age > maxAge;
  }

  async refreshMembers(): Promise<User[]> {
    const groupId = this.getGroupId();
    const result = await this.userGroupService.fetchUserGroup(groupId);
    if (result.success) {
      this.memberCache = result.data;
      localStorage.setItem('app_kdo.groupMembers', JSON.stringify(this.memberCache));
      localStorage.setItem('app_kdo.groupMembers_timestamp', Date.now().toString());
      return this.memberCache;
    }

    console.warn('[GroupContext] Échec du refresh des membres');
    this.memberCache = [];
    localStorage.removeItem('groupMembers');
    localStorage.removeItem('groupMembers_timestamp');
    return [];
  }

}
