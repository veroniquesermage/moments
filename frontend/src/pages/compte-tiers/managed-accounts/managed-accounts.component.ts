import {Component, computed, OnInit} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {UserTiersRequest} from 'src/core/models/user-tiers-request.model';
import {CommonModule} from '@angular/common';
import {UserService} from 'src/core/services/user.service';
import {ErrorService} from 'src/core/services/error.service';
import {AuthService} from 'src/security/service/auth.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-managed-accounts',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    FormsModule,
    CommonModule
  ],
  templateUrl: './managed-accounts.component.html',
  styleUrl: './managed-accounts.component.scss'
})
export class ManagedAccountsComponent implements OnInit{
  givenName: string ='';
  familyName: string ='';
  nickname: string ='';
  managedAccounts = computed(() => this.userService.userTiersResponse());

  constructor(private userService: UserService,
              private errorService: ErrorService,
              private authService: AuthService,
              public router: Router) {
  }

  async ngOnInit() {
    const success = await this.userService.loadAllUserTiers();
    if (!success) {
      this.errorService.showError("Impossible de charger les comptes tiers.");
    }
  }

  async goToCreateCompteTiers() {
    const userTiers: UserTiersRequest = {
      nom: this.familyName,
      prenom: this.givenName,
      surnom: this.nickname
    }
    const response = await this.userService.createUserTiers(userTiers);

    if (response.success){
      await this.userService.loadAllUserTiers();

      this.givenName = '';
      this.familyName = '';
      this.nickname = '';
    } else {
      this.errorService.showError(response.message ?? "Une erreur inconnue est survenue");
    }

  }

  async switchToAccount(id: number) {
    try{
      await this.authService.switchToAccount(id);
      void this.router.navigate(['dashboard']);

    } catch (e) {
      this.errorService.showError("Une erreur s'est produite, veuillez réessayer.")
    }
  }
}
