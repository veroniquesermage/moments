import {Component, effect, Input, Signal} from '@angular/core';
import {UserDisplay} from 'src/core/models/user-display.model';
import {CommonModule} from '@angular/common';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';
import {FormsModule} from '@angular/forms';
import {UserGroupService} from 'src/core/services/user-group.service';
import {ErrorService} from 'src/core/services/error.service';
import {GroupContextService} from 'src/core/services/group-context.service';

@Component({
  selector: 'app-group-roles',
  standalone: true,
  imports: [
    CommonModule,
    DisplayNamePipe,
    FormsModule,
  ],
  templateUrl: './group-roles.component.html',
  styleUrl: './group-roles.component.scss'
})
export class GroupRolesComponent {

  @Input()
  membersSignal!: Signal<UserDisplay[]>;
  @Input()
  groupId: number | undefined;

  membersEdition: UserDisplay[] = [];
  changes: UserDisplay[] = [];
  roles = ['ADMIN', 'MEMBRE'];
  showMemberModal = false;

  constructor(private userGroupService: UserGroupService,
              private errorService: ErrorService,
              private groupContextService: GroupContextService) {
  }

  private _syncMembersEffect = effect(() => {
    if (this.membersSignal) {
      this.membersEdition = this.membersSignal().map(m => ({ ...m }));
    }
  });

  private buildRoleChanges(): void {
     for (const edited of this.membersEdition) {
      const original = this.membersSignal().find(o => o.id === edited.id);
      if (original && original.role !== edited.role) {
        this.changes.push(edited);
      }
    }
  }

  confirmRole() {
    this.buildRoleChanges()
    this.showMemberModal = true;
  }

  cancel() {
    this.changes = [];
    this.showMemberModal = false;
  }

  async validation() {
    const result = await this.userGroupService.updateRoleUsers(this.groupId!, this.changes);
    if(result.success){
      await this.groupContextService.updateMemberSignal();
      this.cancel()
    } else {
      this.errorService.showError(result.message);
    }
  }

}
