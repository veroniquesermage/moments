import {Injectable, Signal, signal} from '@angular/core';
import {Router} from '@angular/router';
import {UserDisplay} from 'src/core/models/user-display.model';
import {UserService} from 'src/core/services/user.service';

@Injectable({ providedIn: 'root' })
export class GroupContextService{

  membersSignal = signal<UserDisplay[]>([]);

  constructor(private userService: UserService,
              private router: Router) {}

  async setGroupContext(id: number): Promise<void> {
    const groupUsers = await this.userService.fetchUserGroup(id);
    if (groupUsers.success) {
      this.membersSignal.set(groupUsers.data);
    } else {
      console.warn('[GroupContext] Échec du fetch des membres pour le groupe', id);
    }
    const safeId = Number(id);
    localStorage.setItem('app_kdo.activeGroupId', safeId.toString());
  }

  getGroupId(): number | null {
    const id = localStorage.getItem('app_kdo.activeGroupId');
    if (!id || isNaN(Number(id))) {
      void this.router.navigate(['/groupe/onboarding']);
      return null;
    }
    return Number(id);
  }

  getMembersSignal(): Signal<UserDisplay[]> {
    return this.membersSignal;
  }

  async updateMemberSignal() {
    const id = this.getGroupId();
    if (!id) {
      this.membersSignal.set([]);
      return;
    }

    const groupUsers = await this.userService.fetchUserGroup(id);
    if (groupUsers.success) {
      this.membersSignal.set(groupUsers.data);
    }
  }

  clearGroupCache(){
    localStorage.removeItem('app_kdo.activeGroupId');
    this.membersSignal.set([]);
  }

}
