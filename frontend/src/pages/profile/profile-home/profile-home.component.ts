import { Component } from '@angular/core';
import {CommonModule} from '@angular/common';
import {ProfileAccountComponent} from 'src/pages/profile/profile-account/profile-account.component';
import {ProfileGroupComponent} from 'src/pages/profile/profile-group/profile-group.component';
import {ProfileActionsComponent} from 'src/pages/profile/profile-actions/profile-actions.component';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {ErrorService} from 'src/core/services/error.service';

@Component({
  selector: 'app-profile-home',
  standalone: true,
  imports: [
    CommonModule,
    ProfileAccountComponent,
    ProfileGroupComponent,
    ProfileActionsComponent,
    TerminalModalComponent
  ],
  templateUrl: './profile-home.component.html',
  styleUrl: './profile-home.component.scss'
})
export class ProfileHomeComponent {

  constructor( public errorService: ErrorService ) {
  }
}
