import {Component, inject, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {Gift} from 'src/core/models/gift.model';
import {GiftFormComponent} from 'src/shared/components/gift-form/gift-form.component';
import {NgIf} from '@angular/common';
import {GiftService} from 'src/core/services/gift.service';

@Component({
  selector: 'app-gift-update',
  imports: [
    GiftFormComponent,
    NgIf
  ],
  templateUrl: './gift-update.component.html',
  styleUrl: './gift-update.component.scss'
})
export class GiftUpdateComponent implements OnInit{

  errorMessage: string | null = null;
  private route = inject(ActivatedRoute);
  id: number | undefined = undefined;
  gift: Gift | undefined = undefined;

  constructor(private giftService: GiftService,
              public router: Router,) {
  }

  async ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.id = idParam ? +idParam : undefined;

    if(!this.id){
      this.giftService.errorMessage.set("❌ Impossible de modifier le cadeau.");
      return;
    }
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.gift = result.data;
    }
  }

  async onSubmit(giftFormData: Gift) {
    const gift: Gift = {
      ...this.gift!,
      ...giftFormData
    };

    await this.giftService.updateGift(gift);
    await this.router.navigate(['/dashboard/mes-cadeaux']);

  }

}
