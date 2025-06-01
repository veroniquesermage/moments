import {Component, inject, OnInit} from '@angular/core';
import {NgIf} from "@angular/common";
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {ActivatedRoute, Router} from '@angular/router';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GiftStatutDTO} from "src/core/models/gift/gift-statut.model";
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftDeliveryUpdate} from 'src/core/models/gift/gift-delivery-update.model';

@Component({
  selector: 'app-gift-follow-up-table',
  standalone: true,
  imports: [
    NgIf,
    TerminalModalComponent
  ],
  templateUrl: './gift-follow-up-detail.component.html',
  styleUrl: './gift-follow-up-detail.component.scss'
})
export class GiftFollowUpDetailComponent implements OnInit{

  gift: GiftPublicResponse | undefined = undefined;
  private route = inject(ActivatedRoute);
  private giftId: number | undefined;
  protected readonly GiftStatus = GiftStatus;

  constructor(public giftService: GiftService,
              public errorService: ErrorService,
              public router: Router) {

    const idParam = this.route.snapshot.paramMap.get('id');
    this.giftId = idParam ? +idParam : undefined;
  }

  async ngOnInit(): Promise<void> {

    if(!this.giftId){
      this.errorService.showError("❌ Une erreur s''est produite. Veuillez réessayer plus tard." );
    } else {
      const result = await this.giftService.getGift(this.giftId);
      if (result.success) {
        this.gift = result.data.gift;
      } else {
        this.errorService.showError(result.message);
      }
    }

  }

  back(){
    this.router.navigate(['/dashboard/cadeaux-suivis']);
  }

  async changeStatus(){
    const statut: GiftStatutDTO = {status: GiftStatus.DISPONIBLE};
    const result = await this.giftService.changeStatusGift(this.giftId!, statut);
    if(!result.success){
      this.errorService.showError("❌ Erreur lors de l'annulation, veuillez réessayer plus tard.")
    }
    await this.router.navigate(['/dashboard/cadeaux-suivis']);
  }

  addDeliver(){
    this.router.navigate(['/dashboard/cadeaux-suivis/livraison', this.giftId]);
  }

  async confirmReception() {
    const gift = await this.giftService.getGift(this.giftId!);

    if (!gift.success) {
      this.errorService.showError("❌ Impossible de confirmer la réception.");
      return;
    }

    const updatedGift: GiftDeliveryUpdate = {
      lieuLivraison: gift.data.delivery?.lieuLivraison ?? undefined,
      dateLivraison: gift.data.delivery?.dateLivraison ?? undefined,
      prixReel: gift.data.delivery?.prixReel ?? undefined,
      recu: true
    };

    const result = await this.giftService.updateGiftDelivery(this.giftId!, updatedGift);

    if (result.success) {
      await this.giftService.getFollowedGifts();
      // ici tu peux ajouter un toast ou redirection
    } else {
      this.errorService.showError("❌ Échec de la confirmation de réception.");
    }
  }




  cancel(){
    this.router.navigate(['/dashboard/cadeaux-suivis']);
  }
}
