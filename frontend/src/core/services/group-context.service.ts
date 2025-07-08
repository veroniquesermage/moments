import {Injectable, Signal, signal} from '@angular/core';
import {UserGroupService} from 'src/core/services/user-group.service';
import {Router} from '@angular/router';
import {UserDisplay} from 'src/core/models/user-display.model';

@Injectable({ providedIn: 'root' })
export class GroupContextService{

  membersSignal = signal<UserDisplay[]>([]);

  constructor(private userGroupService: UserGroupService,
              private router: Router) {}

  async setGroupContext(id: number): Promise<void> {
    const groupUsers = await this.userGroupService.fetchUserGroup(id);
    if (groupUsers.success) {
      this.membersSignal.set(groupUsers.data);
    } else {
      console.warn('[GroupContext] Échec du fetch des membres pour le groupe', id);
    }
    const safeId = Number(id);
    localStorage.setItem('app_kdo.activeGroupId', safeId.toString());
  }

  getGroupId(): number {
    const id = localStorage.getItem('app_kdo.activeGroupId');
    if (!id || isNaN(Number(id))) {
      this.router.navigate(['/onboarding']);
    }
    return Number(id);
  }

  getMembersSignal(): Signal<UserDisplay[]> {
    return this.membersSignal;
  }

  async updateMemberSignal() {
    const id = this.getGroupId();
    const groupUsers = await this.userGroupService.fetchUserGroup(id);
    if (groupUsers.success) {
      this.membersSignal.set(groupUsers.data);
    }
  }

  clearGroupCache(){
    localStorage.removeItem('app_kdo.activeGroupId');
    this.membersSignal.set([]);
  }

}
