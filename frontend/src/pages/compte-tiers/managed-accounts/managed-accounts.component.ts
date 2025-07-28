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
import {GroupService} from 'src/core/services/group.service';
import {ExportManagedAccountRequest} from 'src/core/models/export-managed-account-request.model';
import {ToastrService} from 'ngx-toastr';
import {GroupResume} from 'src/core/models/group/group-resume.model';
import {GroupContextService} from 'src/core/services/group-context.service';

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
  selectedAccount?: number;
  showExportUser: boolean = false;
  selectedGroupId: number | undefined;
  groupes = computed(() => this.groupService.groupes());
  groupFiltered: GroupResume[] = [];

  constructor(private userService: UserService,
              private groupService: GroupService,
              private groupContextService :GroupContextService,
              private userGroupService: UserGroupService,
              public errorService: ErrorService,
              private authService: AuthService,
              private toastr: ToastrService,
              public router: Router) {
  }

  async ngOnInit() {
    const success = await this.userService.loadAllUserTiers();
    if (!success) {
      this.errorService.showError("Impossible de charger les comptes tiers.");
    }
    const groupId = this.groupContextService.getGroupId();
    this.groupFiltered = this.groupes().filter(gr => gr.id != groupId);

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

  addToAnotherGroup(id: number) {
    this.selectedAccount = id;
    this.showExportUser = true;
  }

  deleteFromGroup(id: number) {
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

  deleteGlobally(id: number) {
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
    if(!this.selectedAccount){
      this.errorService.showError("Une erreur est survenue, veuillez réessayer.")
    }
    const result = await this.userGroupService.removeTiersFromGroup(this.selectedAccount!)
    if(result.success){
      this.selectedAccount = undefined;
      const success = await this.userService.loadAllUserTiers();
      if (!success) {
        this.errorService.showError("Impossible de charger les comptes tiers.");
      }
    } else {
      this.errorService.showError(result.message);
    }
  }

  async confirmDeleteGlobally() {
    if(!this.selectedAccount){
      this.errorService.showError("Une erreur est survenue, veuillez réessayer.")
    }
    const result = await this.userService.deleteManagedAccount(this.selectedAccount!);
    if(result.success){
      this.selectedAccount = undefined;
      const success = await this.userService.loadAllUserTiers();
      if (!success) {
        this.errorService.showError("Impossible de charger les comptes tiers.");
      }
    } else {
      this.errorService.showError(result.message);
    }
  }

  async confirmExport() {
    if(!this.selectedAccount || !this.selectedGroupId){
      this.errorService.showError("Une erreur est survenue, veuillez réessayer.");
    }
    const request: ExportManagedAccountRequest = {
      userId: this.selectedAccount!,
      groupId: this.selectedGroupId!
    }
    const result = await this.userGroupService.exportTiersToGroup(request);
    if(result.success){
      this.toastr.success("L'opération s'est terminée avec succès !");
      this.showExportUser = false;
    } else {
      this.showExportUser = false;
      this.errorService.showError(result.message);
    }
  }

  cancelExport() {
    this.selectedAccount = undefined;
    this.showExportUser = false;
  }

  return() {
    void this.router.navigate(['/dashboard']);
  }

}
