import {Component, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {User} from 'src/security/model/user.model';
import {ErrorService} from 'src/core/services/error.service';
import {AuthService} from 'src/security/service/auth.service';
import {Router} from '@angular/router';

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

  user: User | null = null ;

  constructor(public errorService: ErrorService,
              private authService: AuthService,
              public router: Router) {
  }

  async ngOnInit() {
    this.user = this.authService.profile();
    if(this.user == null){
      this.errorService.showError("❌ Impossible d\'afficher les infos de ce membre. Veuillez réessayer plus tard.")
    }
  }

  async disconnect() {
    await this.authService.logout()
  }

  changePassword() {
    void this.router.navigate(['/auth/reset-password'], {
      queryParams: {context: 'change'}
    });
  }
}
