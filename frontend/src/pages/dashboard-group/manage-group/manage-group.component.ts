import {Component, OnInit, signal} from '@angular/core';
import {GroupInfoComponent} from 'src/pages/dashboard-group/group-info/group-info.component';
import {GroupContextService} from 'src/core/services/group-context.service';
import {GroupInviteComponent} from 'src/pages/dashboard-group/group-invite/group-invite.component';
import {UserDisplay} from 'src/core/models/user-display.model';
import {GroupRolesComponent} from 'src/pages/dashboard-group/group-roles/group-roles.component';
import {GroupActionsComponent} from 'src/pages/dashboard-group/group-actions/group-actions.component';
import {UserService} from 'src/core/services/user.service';

@Component({
  selector: 'app-manage-group',
  standalone: true,
  imports: [
    GroupInfoComponent,
    GroupInviteComponent,
    GroupRolesComponent,
    GroupActionsComponent
  ],
  templateUrl: './manage-group.component.html',
  styleUrl: './manage-group.component.scss'
})
export class ManageGroupComponent implements OnInit{

  members = signal<UserDisplay[]>([]);
  composant: string = 'ManageGroupComponent';
  groupId: number | undefined;
  isLoadingMembers = signal<boolean>(false);

  constructor(private groupServiceContext: GroupContextService,
              private userService: UserService) {
  }

  async ngOnInit() {
    this.groupId = this.groupServiceContext.getGroupId() || undefined;
    await this.loadMembers();
  }

  async reloadMembers() {
    await this.loadMembers();
  }

  private async loadMembers(): Promise<void> {
    if (!this.groupId) return;

    this.isLoadingMembers.set(true);
    try {
      const result = await this.userService.fetchUserGroup(this.groupId);
      if (result.success) {
        this.members.set(result.data);
      }
    } catch (error) {
      console.error('[ManageGroupComponent] Erreur lors du chargement des membres:', error);
    } finally {
      this.isLoadingMembers.set(false);
    }
  }
}
