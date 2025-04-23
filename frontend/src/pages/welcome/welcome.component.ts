import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';
import {AuthService} from 'src/security/service/auth.service';
import {LoadingComponent} from 'src/shared/components/loading/loading.component';
import {GroupService} from 'src/core/services/group.service';

@Component({
  selector: 'app-welcome',
  standalone: true,
  templateUrl: './welcome.component.html',
  styleUrls: ['./welcome.component.scss'],
  imports: [CommonModule, LoadingComponent],
})
export class WelcomeComponent {
  constructor(public auth: AuthService, public groupeService: GroupService) {
  }
}

