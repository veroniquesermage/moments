import {Component, OnInit} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {GroupContextService} from 'src/core/services/group-context.service';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {GroupDetail} from 'src/core/models/group/group-detail.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FeedbackTestComponent],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit{

  composant: string = "DashboardComponent";
  selectedGroup: GroupDetail | undefined = undefined;
  isAdmin = false;

  constructor(
    public groupService: GroupService,
    public router: Router,
    public groupContextService: GroupContextService
  ) {
  }

  async ngOnInit() {
    const groupId = this.groupContextService.getGroupId();
    const result = await this.groupService.getGroupDetail(groupId);

    if(result.success){
      this.selectedGroup = result.data;
      this.isAdmin = this.selectedGroup.role == 'ADMIN';
    }
  }

  goToMesCadeaux() {
    this.router.navigate(['dashboard', 'mes-cadeaux']);
  }


  goToListesMembres() {
    this.router.navigate(['dashboard', 'leurs-cadeaux']);

  }

  goToSuiviCadeaux() {
    this.router.navigate(['dashboard', 'cadeaux-suivis']);
  }

  goToIdeeCadeaux(){
    this.router.navigate(['dashboard', 'idees']);
  }

  goToProfile() {
    this.router.navigate(['profile']);
  }
  goToGestionGroupe() {
    this.router.navigate(['/groupe/admin']);
  }


}
