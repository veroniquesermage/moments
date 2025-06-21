import {Component, OnInit} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {ErrorService} from 'src/core/services/error.service';
import {GroupContextService} from 'src/core/services/group-context.service';
import {GroupDetail} from 'src/core/models/group-detail.model';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {UserGroupService} from 'src/core/services/user-group.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';
import {Router} from '@angular/router';
import {UserDisplay} from 'src/core/models/user-display.model';

@Component({
  selector: 'app-profile-group',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    TerminalModalComponent
  ],
  templateUrl: './profile-group.component.html',
  styleUrl: './profile-group.component.scss'
})
export class ProfileGroupComponent implements OnInit{

  group: GroupDetail | undefined
  members: string[] = []
  allMembers: UserDisplay[] = []
  showMemberModal: boolean = false;
  showNicknameModal: boolean = false;
  showConfirmModal: boolean = false;
  nickname: string = "";
  message: string = "Etes vous sûr de vouloir quitter définitivement le groupe ?"
  modalActions: TerminalModalAction[] = [{ label: 'Quitter le groupe', eventName: 'QUITTER', style: 'danger' },
                                        { label: 'Annuler', eventName: 'CANCEL', style: 'primary' }];

  constructor(private groupService: GroupService,
              private userGroupService: UserGroupService,
              public errorService: ErrorService,
              private router: Router,
              private groupContextService: GroupContextService) {}

  async ngOnInit(){
      await this.loadGroupDetail();
  }

  async getAllMembers() {
    this.allMembers = await this.groupContextService.getGroupMembers();

    this.showMemberModal = true;
  }

  cancel() {
    this.showMemberModal = false;
    this.showNicknameModal = false;

    if (this.group!.surnom){
      this.nickname = this.group!.surnom;
    }
  }

  async updateNickname() {
    this.showNicknameModal = true;
  }

  async confirmNickname() {
    const result = await this.userGroupService.updateNickname(this.groupContextService.getGroupId(), this.nickname);

    if(result.success){
      await this.loadGroupDetail();
      this.showNicknameModal = false;
    } else {
      this.showNicknameModal = false;
      this.errorService.showError(result.message);
    }
  }

  async leaveGroup() {
    if(await this.hasAnotherAdminsInGroup()){
      this.showConfirmModal = true;
    } else {
      this.message = "Vous êtes le seul administrateur du groupe, vous devez d'abord nommer un nouvel admin";
      this.modalActions = [{ label: 'Annuler', eventName: 'CANCEL', style: 'primary' }];
      this.showConfirmModal = true;
    }
  }

  async handleClicked(eventName: string) {
    if(eventName === 'CANCEL'){
      this.showConfirmModal = false;
    }
    try {
      await this.userGroupService.deleteUserInGroup(this.groupContextService.getGroupId());
      await this.router.navigate(['/groupe/onboarding']);
      this.showConfirmModal = false;
    } catch (err) {
      this.errorService.showError("❌ Une erreur est survenue en quittant le groupe.");
    }
  }

  async loadGroupDetail(){
    const result = await this.groupService.getGroupDetail(this.groupContextService.getGroupId());
    if(result.success){
      this.group = result.data;
      if (this.group.surnom){
        this.nickname = this.group.surnom;
      }
    } else {
      this.errorService.showError(result.message);
    }
  }

  async hasAnotherAdminsInGroup() {
    const result = await this.userGroupService.getUser();
    if (!result.success) {
      this.errorService.showError(result.message);
      return false;
    }

    const currentUserId = result.data.id;

    // Si je ne suis pas admin, je peux partir
    if (this.group?.role !== 'ADMIN') return true;

    // Je suis admin, je vérifie s’il y a d’autres admins
    const otherAdmins = this.group.admins.filter(admin => admin.id !== currentUserId);
    return otherAdmins.length > 0;
  }


}
