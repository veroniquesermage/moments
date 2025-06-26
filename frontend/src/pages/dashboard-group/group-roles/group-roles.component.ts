import {Component, Input, OnChanges, SimpleChanges} from '@angular/core';
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
export class GroupRolesComponent implements OnChanges {

  @Input()
  membersOriginal: UserDisplay[] = [];
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

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['membersOriginal']?.currentValue) {
      const original: UserDisplay[] = changes['membersOriginal'].currentValue;
      this.membersEdition = original.map(m => ({ ...m }));
    }
  }

  private buildRoleChanges(): void {
     for (const edited of this.membersEdition) {
      const original = this.membersOriginal.find(o => o.id === edited.id);
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
    this.membersOriginal = this.membersEdition.map(m => ({ ...m }));
    const result = await this.userGroupService.updateRoleUsers(this.groupId!, this.changes);
    if(result.success){
      this.groupContextService.updateMemberCache(result.data);
      this.cancel()
    } else {
      this.errorService.showError(result.message);
    }
  }

}
