import {Component, EventEmitter, inject, Input, OnInit, Output} from '@angular/core';
import {NgIf} from "@angular/common";
import {GiftService} from 'src/core/services/gift.service';
import {Gift} from 'src/core/models/gift.model';
import {ErrorService} from 'src/core/services/error.service';
import {ActivatedRoute, Router} from '@angular/router';
import {GiftStatutDTO} from 'src/core/models/gift-statut.model';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';

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

  gift: Gift | undefined = undefined;
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
        this.gift = result.data;
      } else {
        this.errorService.showError(result.message);
      }
    }

  }

  back(){
    this.router.navigate(['/dashboard/cadeaux-suivis']);
  }

  async changeStatus(status : GiftStatus){
    const statut: GiftStatutDTO = {status: GiftStatus.DISPONIBLE};
    const result = await this.giftService.changerStatutGift(this.giftId!, statut);
    if(!result.success){
      this.errorService.showError("❌ Erreur lors de l'annulation, veuillez réessayer plus tard.")
    }
    await this.router.navigate(['/dashboard/cadeaux-suivis']);
  }

  addDeliver(){
    this.router.navigate(['/dashboard/cadeaux-suivis/livraison', this.giftId]);
  }
}
