import {Component, computed, OnInit} from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {UserTiersRequest} from 'src/core/models/user-tiers-request.model';
import {CommonModule} from '@angular/common';
import {UserService} from 'src/core/services/user.service';
import {ErrorService} from 'src/core/services/error.service';
import {AuthService} from 'src/security/service/auth.service';
import {Router} from '@angular/router';
import {UserGroupService} from 'src/core/services/user-group.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';
import {ModalActionType} from 'src/core/enum/modal-action.enum';

@Component({
  selector: 'app-managed-accounts',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    FormsModule,
    CommonModule,
    TerminalModalComponent
  ],
  templateUrl: './managed-accounts.component.html',
  styleUrl: './managed-accounts.component.scss'
})
export class ManagedAccountsComponent implements OnInit{
  givenName: string ='';
  familyName: string ='';
  nickname: string ='';
  managedAccounts = computed(() => this.userService.userTiersResponse());
  showModal: boolean = false;
  message: string = '';
  modalActions:  TerminalModalAction[] = [];
  selectedAccount: number = 0;

  constructor(private userService: UserService,
              private userGroupService: UserGroupService,
              public errorService: ErrorService,
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
      await this.authService.switchToTiers(id);
      void this.router.navigate(['dashboard']);
    } catch (e) {
      this.errorService.showError("Une erreur s'est produite, veuillez réessayer.")
    }
  }

  return() {
    void this.router.navigate(['/dashboard']);
  }

  async deleteFromGroup(id: number) {
    this.selectedAccount = id;
    this.showModal = true;
    const user =  this.managedAccounts().find(account => account.id == id)
    if (!user) {
      this.errorService.showError("Ce compte tiers est introuvable.");
      return;
    }
    this.message = `Êtes-vous sûr de vouloir supprimer le compte tiers de ${user?.prenom} ${user?.nom || ''} ?`;
    this.modalActions = [{ label: 'Supprimer du groupe', eventName: 'DELETE_FROM_GROUP', style: 'danger' },
      { label: 'Annuler', eventName: 'CANCEL', style: 'primary' }];
  }

  async deleteGlobally(id: number) {
    this.selectedAccount = id;
    this.showModal = true;
    const user =  this.managedAccounts().find(account => account.id == id)
    this.message = `Êtes-vous sûr de vouloir supprimer définitivement le compte tiers de ${user?.prenom} ${user?.nom || ''} ? <br> Cette action est irréversible.`;
    this.modalActions = [{ label: 'Supprimer définitivement', eventName: 'DELETE', style: 'danger' },
      { label: 'Annuler', eventName: 'CANCEL', style: 'primary' }];
  }

  async handleClicked(eventName: string) {
    if (eventName === ModalActionType.DELETE) {
      await this.confirmDeleteGlobally();
    } else if (eventName === ModalActionType.DELETE_FROM_GROUP) {
      await this.confirmDeleteFromGroup();
    }
    this.showModal = false;
  }

  async confirmDeleteFromGroup(){
    const result = await this.userGroupService.removeTiersFromGroup(this.selectedAccount)
    if(result.success){
      const success = await this.userService.loadAllUserTiers();
      if (!success) {
        this.errorService.showError("Impossible de charger les comptes tiers.");
      }
    } else {
      this.errorService.showError(result.message);
    }
  }

  async confirmDeleteGlobally() {
    const result = await this.userService.deleteManagedAccount(this.selectedAccount);
    if(result.success){
      const success = await this.userService.loadAllUserTiers();
      if (!success) {
        this.errorService.showError("Impossible de charger les comptes tiers.");
      }
    } else {
      this.errorService.showError(result.message);
    }
  }
}
