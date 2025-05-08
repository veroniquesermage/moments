import {Component, computed} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';
import {GroupStateService} from 'src/core/services/groupState.service';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {

  selectedGroup = computed(() => this.groupState.selectedGroup());
  estAdmin = true;

  constructor(
    public groupService: GroupService,
    public router: Router,
    public groupState: GroupStateService
  ) {
  }

  goToMesCadeaux() {
    this.router.navigate(['dashboard', 'mes-cadeaux']);
  }


  goToListesMembres() {

  }

  goToChangerGroupe() {

  }

  goToGestionGroupe() {

  }

  envoyerFeedback() {

  }
}
