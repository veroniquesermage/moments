import {Component, computed, inject, OnInit} from '@angular/core';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {FormControl, FormGroup, FormsModule, ReactiveFormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {ActivatedRoute, Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {GiftPurchaseInfoSchema} from 'src/core/models/gift/gift-purchase-info.model';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';
import {GiftPurchaseUpdate} from 'src/core/models/gift/gift-purchase-update.model';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {UserService} from 'src/core/services/user.service';
import {UserTiersResponse} from 'src/core/models/user-tiers-response.model';

@Component({
  selector: 'app-gift-purchase',
  standalone: true,
  imports: [
    FeedbackTestComponent,
    FormsModule,
    ReactiveFormsModule,
    TerminalModalComponent,
    DisplayNamePipe,
    CommonModule
  ],
  templateUrl: './gift-purchase.component.html',
  styleUrl: './gift-purchase.component.scss'
})
export class GiftPurchaseComponent implements OnInit{

  purchaseForm: FormGroup<{
    commentaire: FormControl<string>;
    compteTiers: FormControl<UserTiersResponse | null>;
    prixReel: FormControl<number | undefined>;
  }>;

  private route = inject(ActivatedRoute);
  id?: number;
  giftDetail?: GiftDetailResponse;
  purchase?: GiftPurchaseInfoSchema;
  managedAccounts = computed(() => this.userService.userTiersResponse());
  composant: string = "GiftPurchaseComponent";

  constructor(private giftService: GiftService,
              public router: Router,
              public errorService: ErrorService,
              private userService : UserService) {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.id = idParam ? +idParam : undefined;
    this.purchaseForm = new FormGroup({
      commentaire: new FormControl('', {nonNullable: true}),
      compteTiers: new FormControl<UserTiersResponse | null>(null),
      prixReel: new FormControl<number | undefined>(undefined, {nonNullable: true})
    });
  }

  async ngOnInit() {
    if (!this.id) {
      this.errorService.showError("❌ Impossible de modifier le cadeau.");
      return;
    }
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.giftDetail = result.data;
      this.purchase = result.data.purchaseInfo;
    } else {
      this.errorService.showError("❌ Impossible de modifier le cadeau.");
    }

    const success = await this.userService.loadAllUserTiers();
    if (!success) {
      this.errorService.showError("Impossible de charger les comptes tiers.");
    }

    const compteTiersId = this.purchase?.compteTiers?.id;

    const matchedCompteTiers = this.managedAccounts()
      .find(u => u.id === compteTiersId) ?? null;

    this.purchaseForm.patchValue({
      commentaire: this.purchase?.commentaire ?? '',
      compteTiers: matchedCompteTiers,
      prixReel: this.purchase?.prixReel ?? undefined,
    });

  }

  async onSubmit() {
    if (!this.giftDetail) return;

    const updatedPurchase: GiftPurchaseUpdate = {
      giftId: this.id!,
      commentaire: this.purchaseForm.value.commentaire || undefined,
      compteTiers: this.purchaseForm.value.compteTiers || undefined,
      prixReel: Number(this.purchaseForm.value.prixReel)

    }
    const result = await this.giftService.updateGiftPurchase(updatedPurchase);
    if (result.success) {
      await this.giftService.getFollowedGifts();
      this.cancel();
    } else {
      this.errorService.showError(result.message);
    }
  }

  cancel() {
    void this.router.navigate(['/dashboard/cadeau', this.id], {
      queryParams: { context: 'suivi' }
    });
  }

  sanitizeDecimal(event: Event, key: string): void {
    const input = event.target as HTMLInputElement;
    input.value = input.value.replace(',', '.');
    // met à jour le FormControl manuellement
    this.purchaseForm?.get(key)?.setValue(input.value);
  }
}
