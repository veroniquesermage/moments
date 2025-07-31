import {Component, inject, OnInit} from '@angular/core';
import {NgIf} from "@angular/common";
import {TerminalModalComponent} from "src/shared/components/terminal-modal/terminal-modal.component";
import {ActivatedRoute, Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {FormControl, FormGroup, FormsModule, ReactiveFormsModule} from '@angular/forms';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftDeliveryUpdate} from 'src/core/models/gift/gift-delivery-update.model';
import {GiftDelivery} from 'src/core/models/gift/gift-delivery.model';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';

@Component({
  selector: 'app-gift-deliver',
  imports: [
    NgIf,
    TerminalModalComponent,
    FormsModule,
    ReactiveFormsModule,
    FeedbackTestComponent
  ],
  standalone: true,
  templateUrl: './gift-deliver.component.html',
  styleUrl: './gift-deliver.component.scss'
})
export class GiftDeliverComponent implements OnInit {

  giftForm: FormGroup<{
    lieuLivraison: FormControl<string>;
    dateLivraison: FormControl<string>;
    prixReel: FormControl<string>; // on reste en string tant que tu veux gérer les virgules
  }>;

  private route = inject(ActivatedRoute);
  id: number | undefined = undefined;
  gift: GiftPublicResponse | undefined = undefined;
  delivery: GiftDelivery | undefined = undefined;
  composant: string = "GiftDeliverComponent";

  constructor(private giftService: GiftService,
              public router: Router,
              public errorService: ErrorService) {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.id = idParam ? +idParam : undefined;
    this.giftForm = new FormGroup({
      lieuLivraison: new FormControl('', {nonNullable: true}),
      dateLivraison: new FormControl('', {nonNullable: true}),
      prixReel: new FormControl('', {nonNullable: true})
    });
  }

  async ngOnInit() {
    if (!this.id) {
      this.errorService.showError("❌ Impossible de modifier le cadeau.");
      return;
    }
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.gift = result.data.gift;
      this.delivery = result.data.delivery;
      if (this.delivery) {
        this.giftForm.patchValue({
          lieuLivraison: this.delivery.lieuLivraison ?? '',
          dateLivraison: this.delivery.dateLivraison ?? '',
          prixReel: ''
        });
      }
    } else {
      this.errorService.showError("❌ Impossible de modifier le cadeau.");
    }
  }

  async onSubmit() {
    if (!this.gift) return;

    const updatedDelivery: GiftDeliveryUpdate = {
      lieuLivraison: this.giftForm.value.lieuLivraison || null,
      dateLivraison: this.giftForm.value.dateLivraison || null,
      prixReel: Number(this.giftForm.value.prixReel),
      recu: this.delivery?.recu ?? false

    }

    const result = await this.giftService.updateGiftDelivery(this.gift.id!, updatedDelivery);

    if (result.success) {
      await this.giftService.getFollowedGifts();
      this.cancel();
    } else {
      this.errorService.showError(result.message);
    }
  }

  cancel() {
    void this.router.navigate(['/dashboard/cadeaux-suivis']);
  }

  sanitizeDecimal(event: Event, key: string): void {
    const input = event.target as HTMLInputElement;
    input.value = input.value.replace(',', '.');
    // met à jour le FormControl manuellement
    this.giftForm?.get(key)?.setValue(input.value);
  }
}
