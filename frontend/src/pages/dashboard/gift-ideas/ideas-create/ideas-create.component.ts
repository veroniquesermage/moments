import {Component, OnInit} from '@angular/core';
import {TerminalModalComponent} from "src/shared/components/terminal-modal/terminal-modal.component";
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';
import {Router} from '@angular/router';
import {GiftIdeaFormComponent} from 'src/shared/components/gift-idea-form/gift-idea-form.component';
import {GroupContextService} from 'src/core/services/group-context.service';
import {ErrorService} from 'src/core/services/error.service';
import {GiftIdeaCreate} from 'src/core/models/gift/gift-idea-create.model';
import {GiftCreate} from 'src/core/models/gift/gift-create.model';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {IdeaService} from 'src/core/services/idea.service';
import {CommonModule} from '@angular/common';
import {GiftIdeaFormData} from 'src/core/models/gift/idea-form-data.model';
import {UserDisplay} from 'src/core/models/user-display.model';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';

@Component({
  selector: 'app-ideas-create',
  standalone: true,
  imports: [
    TerminalModalComponent,
    GiftIdeaFormComponent,
    CommonModule,
    FeedbackTestComponent
  ],
  templateUrl: './ideas-create.component.html',
  styleUrl: './ideas-create.component.scss'
})
export class IdeasCreateComponent implements OnInit {

  message = 'Souhaitez-vous rendre cette idée visible aux membres du groupe ?\n'
  modalActions: TerminalModalAction[] = [{ label: 'Privé', eventName: 'PRIVATE', style: 'primary' },
                                          { label: 'Public', eventName: 'PUBLIC', style: 'primary' }];
  membersGroup: UserDisplay[] = [];
  giftIdeaCreate: GiftIdeaCreate | undefined;
  showModal = false;
  composant: string = "IdeasCreateComponent";

  constructor(public router: Router,
              private groupContextService: GroupContextService,
              public errorService: ErrorService,
              private ideaService: IdeaService) {
  }

  async ngOnInit() {
    this.membersGroup = await this.groupContextService.getGroupMembers();
  }

  async onSubmit(giftFormData: GiftIdeaFormData): Promise<void> {
    console.log("🔔 Submit déclenché dans le parent !");

    const giftCreate: GiftCreate = {
      destinataireId: giftFormData.destinataireId,
      nom: giftFormData.nom,
      description: giftFormData.description,
      marque: giftFormData.marque,
      magasin: giftFormData.magasin,
      url: giftFormData.url,
      quantite: giftFormData.quantite,
      prix: giftFormData.prix,
      fraisPort: giftFormData.fraisPort,
      commentaire: giftFormData.commentaire,
      priorite: 0,
      statut: GiftStatus.DISPONIBLE,
    };

    this.giftIdeaCreate = {
      gift: giftCreate,
      visibilite: false
    }

    this.showModal = true;
  }

  async handleClicked(eventName: string) {
    if(eventName === 'PUBLIC'){
      this.giftIdeaCreate!.visibilite = true;
    }
    try {
      await this.ideaService.createIdeas(this.giftIdeaCreate!);
      await this.router.navigate(['/dashboard/idees']);
    } catch (err) {
      this.errorService.showError("❌ Une erreur est survenue lors de la création.");
    }

  }

}
