import {Component, OnInit, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {User} from 'src/security/model/user.model';
import {UserGroupService} from 'src/core/services/user-group.service';
import {ErrorService} from 'src/core/services/error.service';
import {AuthService} from 'src/security/service/auth.service';

@Component({
  selector: 'app-profile-account',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './profile-account.component.html',
  styleUrl: './profile-account.component.scss'
})
export class ProfileAccountComponent implements OnInit{

  user: User | undefined
  profile = signal<User | null>(null);
  isLoggedIn = signal<boolean>(false);

  constructor(private userGroupService : UserGroupService,
              public errorService: ErrorService,
              private authService: AuthService) {
  }

  async ngOnInit() {
  const result = await this.userGroupService.getUser()
    if(result.success){
      this.user = result.data
    } else {
      this.errorService.showError("❌ Impossible d\'afficher les infos de ce membre. Veuillez réessayer plus tard.")
    }
  }

  async disconnect() {
    this.authService.logout()
  }
}
