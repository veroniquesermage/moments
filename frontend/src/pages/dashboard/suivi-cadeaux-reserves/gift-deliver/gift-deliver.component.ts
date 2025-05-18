import {Component, inject, OnInit} from '@angular/core';
import {GiftFormComponent} from "src/shared/components/gift-form/gift-form.component";
import {NgIf} from "@angular/common";
import {TerminalModalComponent} from "src/shared/components/terminal-modal/terminal-modal.component";
import {ActivatedRoute, Router} from '@angular/router';
import {Gift} from 'src/core/models/gift.model';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators} from '@angular/forms';

@Component({
  selector: 'app-gift-deliver',
  imports: [
    NgIf,
    TerminalModalComponent,
    FormsModule,
    ReactiveFormsModule
  ],
  standalone: true,
  templateUrl: './gift-deliver.component.html',
  styleUrl: './gift-deliver.component.scss'
})
export class GiftDeliverComponent implements OnInit{

  giftForm: FormGroup<{
    lieuLivraison: FormControl<string>;
    dateLivraison: FormControl<string>;
    prixReel: FormControl<string>; // on reste en string tant que tu veux gérer les virgules
  }>;

  private route = inject(ActivatedRoute);
  id: number | undefined = undefined;
  gift: Gift | undefined = undefined;

  constructor(private giftService: GiftService,
              public router: Router,
              public errorService: ErrorService) {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.id = idParam ? +idParam : undefined;
    this.giftForm = new FormGroup({
      lieuLivraison: new FormControl('', { nonNullable: true }),
      dateLivraison: new FormControl('', { nonNullable: true }),
      prixReel: new FormControl('', { nonNullable: true })
    });
  }

  async ngOnInit() {
    if(!this.id){
      this.errorService.showError("❌ Impossible de modifier le cadeau.");
      return;
    }
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.gift = result.data;
      this.giftForm.patchValue({
        lieuLivraison: this.gift.lieuLivraison ?? '',
        dateLivraison: this.gift.dateLivraison ?? '',
        prixReel: this.gift.prixReel?.toString() ?? ''
      });
    } else {
      this.errorService.showError("❌ Impossible de modifier le cadeau.");
    }
  }

  async onSubmit() {
    if (!this.gift) return;

    const updatedGift: Gift = {
      ...this.gift,
      lieuLivraison: this.giftForm.value.lieuLivraison,
      dateLivraison: this.giftForm.value.dateLivraison,
      prixReel: Number(this.giftForm.value.prixReel),
    };

    const result = await this.giftService.updateGift(updatedGift);
    if (result.success) {
      await this.giftService.recupererCadeauxSuivis();
      this.cancel();
    } else {
      this.errorService.showError(result.message);
    }
  }

  cancel(){
    this.router.navigate(['/dashboard/cadeaux-suivis']);
  }

  sanitizeDecimal(event: Event, key: string ): void {
    const input = event.target as HTMLInputElement;
    input.value = input.value.replace(',', '.');
    // met à jour le FormControl manuellement
    this.giftForm?.get(key)?.setValue(input.value);
  }
}
