import {Component, effect, EventEmitter, Input, Output, OnChanges, SimpleChanges, OnInit, ChangeDetectorRef} from '@angular/core';
import {UserDisplay} from 'src/core/models/user-display.model';
import {CommonModule} from '@angular/common';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';
import {FormsModule} from '@angular/forms';
import {UserGroupService} from 'src/core/services/user-group.service';
import {ErrorService} from 'src/core/services/error.service';

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
export class GroupRolesComponent implements OnInit, OnChanges {

  @Input()
  members: UserDisplay[] = [];
  @Input()
  groupId: number | undefined;
  @Output()
  membersUpdated = new EventEmitter<void>();

  membersEdition: UserDisplay[] = [];
  changes: UserDisplay[] = [];
  roles = ['ADMIN', 'MEMBRE'];
  showMemberModal = false;

  constructor(private userGroupService: UserGroupService,
              private errorService: ErrorService,
              private cdr: ChangeDetectorRef) {
  }

  ngOnInit(): void {
    console.log('[GroupRolesComponent] OnInit - members:', this.members);
    this.changes = [];
    this.initMembersEdition();
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['members'] && this.members) {
      console.log('[GroupRolesComponent] Members updated:', this.members);
      this.initMembersEdition();
    }
  }

  private initMembersEdition(): void {
    if (this.members && this.members.length > 0) {
      console.log('[GroupRolesComponent] Initializing members edition with:', this.members);
      this.membersEdition = this.members.map(m => ({ ...m }));
    }
  }

  private buildRoleChanges(): void {
    console.log('[GroupRoles] Building role changes...');
    this.changes = [];
    for (const edited of this.membersEdition) {
      const original = this.members.find(o => o.id === edited.id);
      if (original && original.role !== edited.role) {
        this.changes.push(edited);
      }
    }
    console.log('[GroupRoles] Final changes:', this.changes);
  }

  onRoleChange(): void {
    this.buildRoleChanges();
    this.cdr.detectChanges();
  }

  confirmRole() {
    this.buildRoleChanges();
    if (this.changes.length > 0) {
      this.showMemberModal = true;
    }
  }

  cancel() {
    this.changes = [];
    this.showMemberModal = false;
  }

  async validation() {
    const result = await this.userGroupService.updateRoleUsers(this.groupId!, this.changes);
    if(result.success){
      this.changes = [];
      this.membersUpdated.emit();
      this.showMemberModal = false;
    } else {
      this.errorService.showError(result.message);
    }
  }

}
