import {Component, inject, OnInit} from '@angular/core';
import {GiftIdeaFormComponent} from 'src/shared/components/gift-idea-form/gift-idea-form.component';
import {NgIf} from '@angular/common';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {ActivatedRoute, Router} from '@angular/router';
import {ErrorService} from 'src/core/services/error.service';
import {GiftService} from 'src/core/services/gift.service';
import {GiftIdeasResponse} from 'src/core/models/gift/gift-ideas-response.model';
import {GiftUpdate} from 'src/core/models/gift/gift-update.model';
import {GiftIdeaFormData} from 'src/core/models/gift/idea-form-data.model';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';

@Component({
  selector: 'app-ideas-update',
  standalone: true,
  imports: [
    GiftIdeaFormComponent,
    NgIf,
    TerminalModalComponent,
    FeedbackTestComponent
  ],
  templateUrl: './ideas-update.component.html',
  styleUrl: './ideas-update.component.scss'
})
export class IdeasUpdateComponent implements OnInit{


  private route = inject(ActivatedRoute);
  id: number | undefined = undefined;
  giftIdeaResponse: GiftIdeasResponse | undefined = undefined;
  composant: string = "IdeasUpdateComponent";

  constructor(public router: Router,
              private giftService: GiftService,
              public errorService: ErrorService) {
  }

  async ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.id = idParam ? +idParam : undefined;

    if(!this.id){
      this.errorService.showError("❌ Impossible de modifier l'idée.");
      return;
    }
    const result = await this.giftService.getGift(this.id);
    if (result.success && result.data.ideas) {
      this.giftIdeaResponse = {
        gift: result.data.gift,
        giftIdea: result.data.ideas
      }
    } else {
      this.errorService.showError("❌ Impossible de modifier l'idée.");
    }
  }

  async onSubmit(giftFormData: GiftIdeaFormData) {
    const gift = this.giftIdeaResponse?.gift;
    if(gift){
      const giftUpdate: GiftUpdate = {
        id: gift.id!,
        destinataireId: gift.destinataire.id,
        nom: giftFormData.nom,
        description: giftFormData.description,
        marque: giftFormData.marque,
        magasin: giftFormData.magasin,
        url: giftFormData.url,
        quantite: giftFormData.quantite,
        prix: giftFormData.prix,
        fraisPort: giftFormData.fraisPort,
        commentaire: giftFormData.commentaire,
        priorite: gift.priorite,
        statut: gift.statut
      };

      const result = await this.giftService.updateGift(giftUpdate);
      if (result.success) {
        await this.router.navigate(['/dashboard/idees']);
      } else {
        this.errorService.showError(result.message);
      }
    } else {
      this.errorService.showError('L\'idée est introuvable.')
    }


  }
}
