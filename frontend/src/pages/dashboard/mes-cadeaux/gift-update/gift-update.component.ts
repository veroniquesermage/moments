import {Component, inject, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {GiftFormComponent} from 'src/shared/components/gift-form/gift-form.component';
import {NgIf} from '@angular/common';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {Gift} from 'src/core/models/gift/gift.model';

@Component({
  selector: 'app-gift-update',
  imports: [
    GiftFormComponent,
    NgIf,
    TerminalModalComponent
  ],
  templateUrl: './gift-update.component.html',
  styleUrl: './gift-update.component.scss'
})
export class GiftUpdateComponent implements OnInit{

  private route = inject(ActivatedRoute);
  id: number | undefined = undefined;
  gift: Gift | undefined = undefined;

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

  async onSubmit(giftFormData: Gift) {
    const gift: Gift = {
      ...this.gift!,
      ...giftFormData
    };

    const result = await this.giftService.updateGift(gift);
    if (result.success) {
      await this.giftService.fetchGifts(); // tu appelles que si c’est réussi et seulement si le composant a besoin
      await this.router.navigate(['/dashboard/mes-cadeaux']);
    } else {
      this.errorService.showError(result.message);
    }

  }

}
