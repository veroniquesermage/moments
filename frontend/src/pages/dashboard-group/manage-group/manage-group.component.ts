import {Component, OnInit} from '@angular/core';
import {GroupInfoComponent} from 'src/pages/dashboard-group/group-info/group-info.component';
import {GroupContextService} from 'src/core/services/group-context.service';
import {GroupInviteComponent} from 'src/pages/dashboard-group/group-invite/group-invite.component';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';

@Component({
  selector: 'app-manage-group',
  standalone: true,
  imports: [
    GroupInfoComponent,
    GroupInviteComponent,
    FeedbackTestComponent
  ],
  templateUrl: './manage-group.component.html',
  styleUrl: './manage-group.component.scss'
})
export class ManageGroupComponent implements OnInit{

  composant: string = 'ManageGroupComponent';
  groupId: number | undefined;

  constructor(private groupServiceContext: GroupContextService) {
  }

  ngOnInit() {
    this.groupId = this.groupServiceContext.getGroupId();
  }
}
