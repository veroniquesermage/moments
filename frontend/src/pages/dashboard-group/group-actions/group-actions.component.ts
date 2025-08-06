import {Component, EventEmitter, Input, Output, Signal} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {GroupContextService} from 'src/core/services/group-context.service';
import {Router} from '@angular/router';
import {CommonModule, UpperCasePipe} from '@angular/common';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';
import {UserDisplay} from 'src/core/models/user-display.model';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {ModalActionType} from 'src/core/enum/modal-action.enum';
import {UserGroupService} from 'src/core/services/user-group.service';

@Component({
  selector: 'app-group-actions',
  standalone: true,
  imports: [
    CommonModule,
    UpperCasePipe,
    TerminalModalComponent,
    ReactiveFormsModule,
    FormsModule
  ],
  templateUrl: './group-actions.component.html',
  styleUrl: './group-actions.component.scss'
})
export class GroupActionsComponent {

  @Input()
  groupId: number | undefined;
  @Input()
  membersSignal!: Signal<UserDisplay[]>;
  @Output() membersUpdated = new EventEmitter<void>();

  selectedMemberID?: number;
  showMemberModal: boolean = false;
  showConfirmModal: boolean = false;
  message: string = '';
  modalActions: TerminalModalAction[] = [{ label: 'Exclure du groupe', eventName: 'EXCLURE', style: 'danger' },
    { label: 'Annuler', eventName: 'CANCEL', style: 'primary' }];

  constructor(private groupService: GroupService,
              private groupContextService: GroupContextService,
              private userGroupService : UserGroupService,
              private router: Router) {
  }

  async delete() {
    if(this.groupId){
        const result = await this.groupService.deleteGroup(this.groupId);
        if(result.success){
          this.groupContextService.clearGroupCache();
          await this.router.navigate(['/groupe/onboarding']);
        }
    }
  }

  async back() {
    await this.router.navigate(['/dashboard']);
  }

  removeUser() {
    this.showMemberModal = true;
  }

  cancel() {
    this.selectedMemberID = undefined;
    this.showMemberModal = false;
  }

  excludeMember() {
    if(this.selectedMemberID){
      const user: UserDisplay | undefined = this.membersSignal().find(m => m.id == this.selectedMemberID);
      this.message = `Etes vous sûr de vouloir exclure définitivement <strong>${user!.prenom} ${user!.nom}</strong> du groupe ?`
      this.showConfirmModal = true;
    }
  }

  async handleClicked(eventName: string) {
    if (eventName === ModalActionType.EXCLURE) {
      const result = await this.userGroupService.deleteUserInGroup(this.groupId!, this.selectedMemberID);
      if(result.success){
        await this.groupContextService.updateMemberSignal();
        this.clearModal();
      }
    } else if (eventName === ModalActionType.CANCEL) {
      this.clearModal();
    }
  }

  clearModal(){
    this.selectedMemberID = undefined;
    this.showConfirmModal = false;
    this.showMemberModal = false;
  }
}
