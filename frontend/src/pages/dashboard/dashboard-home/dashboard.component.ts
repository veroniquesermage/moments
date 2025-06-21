import {Component, OnInit} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {GroupContextService} from 'src/core/services/group-context.service';
import {GroupResume} from 'src/core/models/group-resume.model';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent implements OnInit{

  selectedGroup: GroupResume | undefined = undefined;
  estAdmin = true;

  constructor(
    public groupService: GroupService,
    public router: Router,
    public groupContextService: GroupContextService
  ) {
  }

  async ngOnInit() {
    const groupId = this.groupContextService.getGroupId();
    const result = await this.groupService.getGroup(groupId);

    if(result.success){
      this.selectedGroup = result.data;
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

  }


}
