import {Component, OnInit, Signal} from '@angular/core';
import {GroupInfoComponent} from 'src/pages/dashboard-group/group-info/group-info.component';
import {GroupContextService} from 'src/core/services/group-context.service';
import {GroupInviteComponent} from 'src/pages/dashboard-group/group-invite/group-invite.component';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {UserDisplay} from 'src/core/models/user-display.model';
import {GroupRolesComponent} from 'src/pages/dashboard-group/group-roles/group-roles.component';
import {GroupActionsComponent} from 'src/pages/dashboard-group/group-actions/group-actions.component';

@Component({
  selector: 'app-manage-group',
  standalone: true,
  imports: [
    GroupInfoComponent,
    GroupInviteComponent,
    FeedbackTestComponent,
    GroupRolesComponent,
    GroupActionsComponent
  ],
  templateUrl: './manage-group.component.html',
  styleUrl: './manage-group.component.scss'
})
export class ManageGroupComponent implements OnInit{

  membersSignal: Signal<UserDisplay[]>;
  composant: string = 'ManageGroupComponent';
  groupId: number | undefined;

  constructor(private groupServiceContext: GroupContextService) {
    this.membersSignal = this.groupServiceContext.getMembersSignal();
  }

  async ngOnInit() {
    this.groupId = this.groupServiceContext.getGroupId();
  }

  reloadMembers() {
    this.groupServiceContext.updateMemberSignal();
  }
}
