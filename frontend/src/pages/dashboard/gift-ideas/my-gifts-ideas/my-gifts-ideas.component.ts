import {Component, OnInit} from '@angular/core';
import {NgForOf, NgIf} from '@angular/common';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GiftIdeasResponse} from 'src/core/models/gift/gift-ideas-response.model';
import {IdeaService} from 'src/core/services/idea.service';
import {ErrorService} from 'src/core/services/error.service';
import {Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {GiftStatutDTO} from 'src/core/models/gift/gift-statut.model';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';
import {ModalActionType} from 'src/core/enum/modal-action.enum';
import {User} from 'src/security/model/user.model';
import {FormsModule} from '@angular/forms';
import {UserGroupService} from 'src/core/services/user-group.service';
import {ToastrService} from 'ngx-toastr';

@Component({
  selector: 'app-my-gifts-ideas',
  standalone: true,
  imports: [
    NgForOf,
    NgIf,
    TerminalModalComponent,
    FormsModule
  ],
  templateUrl: './my-gifts-ideas.component.html',
  styleUrl: './my-gifts-ideas.component.scss'
})
export class MyGiftsIdeasComponent implements OnInit {

  giftIdeas: GiftIdeasResponse[] = [];
  message = '';
  modalActions: TerminalModalAction[] = [];
  showModal = false;
  targetVisibilityLabel = '';
  ideaId: number | undefined;
  selectedDestId?: number;
  showDuplicationModal = false;
  allUsers: User[] = [];


  constructor(private ideaService: IdeaService,
              private giftService: GiftService,
              private usersGroupService : UserGroupService,
              private router: Router,
              public errorService: ErrorService,
              private toastr: ToastrService) {
  }

  async ngOnInit() {
    await this.loadIdeas();
  }

  changeVisibility(actualVisibility: boolean, ideaId: number) {
    this.ideaId = ideaId;
    this.targetVisibilityLabel = actualVisibility ? 'privée' : 'publique';
    this.message = `Voulez-vous rendre cette idée ${this.targetVisibilityLabel} ?`;
    this.modalActions = [{label: 'OUI', eventName: ModalActionType.VISIBILITY, style: 'primary'},
      {label: 'NON', eventName: ModalActionType.CANCEL, style: 'primary'}];
    this.showModal = true;

  }

  async duplicateIdea(ideaId: number) {
    this.ideaId = ideaId;
    const result = await this.usersGroupService.getAllUsers();

    if(result.success){
      this.allUsers = result.data;
      this.showDuplicationModal = true;
    } else {
      this.showModal = true;
      this.errorService.showError(result.message);
    }
  }

  async handleClicked(eventName: string) {
    if (eventName === ModalActionType.VISIBILITY) {
      await this.ideaService.changeVisibility(this.ideaId!, this.targetVisibilityLabel != 'privée');
      await this.loadIdeas();
      this.clearIdea();
    } else if (eventName === ModalActionType.CANCEL) {
      this.showModal = false;
      await this.router.navigate(['/dashboard/idees'])
    }
  }

  clearIdea() {
    this.ideaId = undefined;
    this.targetVisibilityLabel = '';
    this.showModal = false;
  }

  onRowClick(gift: GiftIdeasResponse) {
    this.router.navigate(['/dashboard/cadeau', gift.gift.id], {
      queryParams: {context: 'idee-cadeau'}
    });
  }

  return() {
    this.router.navigate(['/dashboard']);
  }

  goToAjout() {
    this.router.navigate(['/dashboard/idees/creer']);
  }

  async takeIt(id: number) {
    const giftStatut: GiftStatutDTO = {
      status: GiftStatus.PRIS
    }
    const result = await this.giftService.changeStatusGift(id, giftStatut);

    if (result.success) {
      await this.loadIdeas();
    } else {
      this.errorService.showError("❌ Erreur lors de la tentative de prendre le cadeau, veuillez réessayer plus tard.")
    }
  }

  async loadIdeas() {
    const result = await this.ideaService.fetchIdeas();
    if (result.success) {
      this.giftIdeas = result.data
    } else {
      this.errorService.showError(result.message);
    }
  }

  async confirmDuplication() {

    if(!this.selectedDestId){
      this.showDuplicationModal = false;
      this.errorService.showError("Un destinataire est obligatoire.")
    }
    const result = await this.ideaService.duplicateIdea(this.ideaId!, this.selectedDestId!);

    if(result.success){
      await this.loadIdeas()
      this.toastr.success('Duplication confirmée 👍');
      this.showDuplicationModal = false;
      await this.router.navigate(['/dashboard/idees'])
    } else {
      this.showDuplicationModal = false;
      this.errorService.showError(result.message);
    }
  }

  async cancelDuplication() {
    this.showDuplicationModal = false;
    await this.router.navigate(['/dashboard/idees'])
  }
}
