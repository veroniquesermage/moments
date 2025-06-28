import {Component, Input} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {GroupContextService} from 'src/core/services/group-context.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-group-actions',
  standalone: true,
  imports: [],
  templateUrl: './group-actions.component.html',
  styleUrl: './group-actions.component.scss'
})
export class GroupActionsComponent {

  @Input()
  groupId: number | undefined;

  constructor(private groupService: GroupService,
              private groupContextService: GroupContextService,
              private router: Router) {
  }

  async delete() {
    if(this.groupId){
        const result = await this.groupService.deleteGroup(this.groupId);

        if(result.success){
          this.groupContextService.clearGroupCache();
          await this.router.navigate(['/groupe/onboarding']);
        }
    }
  }

  async back() {
    await this.router.navigate(['/dashboard']);
  }
}
