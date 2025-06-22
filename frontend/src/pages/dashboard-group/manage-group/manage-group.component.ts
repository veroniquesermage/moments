import {Component, OnInit} from '@angular/core';
import {GroupInfoComponent} from 'src/pages/dashboard-group/group-info/group-info.component';
import {GroupContextService} from 'src/core/services/group-context.service';

@Component({
  selector: 'app-manage-group',
  standalone: true,
  imports: [
    GroupInfoComponent
  ],
  templateUrl: './manage-group.component.html',
  styleUrl: './manage-group.component.scss'
})
export class ManageGroupComponent implements OnInit{

  groupId: number | undefined;

  constructor(private groupServiceContext: GroupContextService) {
  }

  ngOnInit() {
    this.groupId = this.groupServiceContext.getGroupId();
  }
}
