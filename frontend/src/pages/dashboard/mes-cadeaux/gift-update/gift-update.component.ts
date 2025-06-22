import {Component, inject, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {GiftFormComponent} from 'src/shared/components/gift-form/gift-form.component';
import {NgIf} from '@angular/common';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GiftUpdate} from 'src/core/models/gift/gift-update.model';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftResponse} from 'src/core/models/gift/gift-response.model';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';

@Component({
  selector: 'app-gift-update',
  imports: [
    GiftFormComponent,
    NgIf,
    TerminalModalComponent,
    FeedbackTestComponent
  ],
  templateUrl: './gift-update.component.html',
  styleUrl: './gift-update.component.scss'
})
export class GiftUpdateComponent implements OnInit{

  private route = inject(ActivatedRoute);
  id: number | undefined = undefined;
  gift: GiftPublicResponse | undefined = undefined;
  composant: string = "GiftUpdateComponent";

  constructor(private giftService: GiftService,
              public router: Router,
              public errorService: ErrorService) {
  }

  async ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.id = idParam ? +idParam : undefined;

    if(!this.id){
      this.errorService.showError("❌ Impossible de modifier le cadeau.");
      return;
    }
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.gift = result.data.gift;
    } else {
      this.errorService.showError("❌ Impossible de modifier le cadeau.");
    }
  }

  async onSubmit(giftFormData: GiftResponse) {
    const giftUpdate: GiftUpdate = {
      id: this.gift!.id!,
      destinataireId: this.gift!.destinataire.id,
      nom: giftFormData.nom,
      description: giftFormData.description,
      marque: giftFormData.marque,
      magasin: giftFormData.magasin,
      url: giftFormData.url,
      quantite: giftFormData.quantite,
      prix: giftFormData.prix,
      fraisPort: giftFormData.fraisPort,
      commentaire: giftFormData.commentaire,
      priorite: this.gift!.priorite,
      statut: this.gift!.statut
    };

    const result = await this.giftService.updateGift(giftUpdate);
    if (result.success) {
      await this.router.navigate(['/dashboard/mes-cadeaux']);
    } else {
      this.errorService.showError(result.message);
    }

  }

}
