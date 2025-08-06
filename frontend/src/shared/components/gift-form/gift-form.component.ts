import {Component, EventEmitter, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {GiftResponse} from 'src/core/models/gift/gift-response.model';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {ErrorService} from 'src/core/services/error.service';

@Component({
  selector: 'app-gift-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './gift-form.component.html',
  styleUrl: './gift-form.component.scss'
})
export class GiftFormComponent implements OnChanges{

  giftForm: FormGroup;
  @Input() gift: GiftPublicResponse | undefined = undefined;
  @Output() formSubmitted = new EventEmitter<GiftResponse>();
  @Output() cancel = new EventEmitter<void>();


  constructor(private fb: FormBuilder,
              public router: Router,
              public errorService : ErrorService) {
    this.giftForm = this.createGiftForm(this.gift);
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['gift'] && this.gift) {
      this.giftForm.patchValue(this.gift);
    }
  }

  onSubmit(): void {
    if (this.giftForm.valid) {
      this.formSubmitted.emit(this.giftForm.value as GiftResponse);
    }
  }

  private createGiftForm(gift: GiftPublicResponse | undefined): FormGroup {
    return new FormGroup({
      id: new FormControl(gift?.id ?? ''),
      nom: new FormControl(gift?.nom ?? '', Validators.required),
      marque: new FormControl(gift?.marque ?? ''),
      magasin: new FormControl(gift?.magasin ?? ''),
      description: new FormControl(gift?.description ?? ''),
      url: new FormControl(gift?.url ?? ''),
      quantite: new FormControl(gift?.quantite ?? 1, Validators.required),
      prix: new FormControl(gift?.prix ?? 0),
      fraisPort: new FormControl(gift?.fraisPort ?? 0),
      commentaire: new FormControl(gift?.commentaire ?? '')
    });
  }

  sanitizeDecimal(event: Event, key: string): void {
    const MAX_AMOUNT = 99999999;
    const input = event.target as HTMLInputElement;

    // Nettoyage : supprime tous les espaces (normaux et insécables)
    let cleaned = input.value.replace(/\s/g, '').replace(/\u00A0/g, '');

    // Remplace virgule par point
    cleaned = cleaned.replace(',', '.');

    // Parse en nombre
    const valueAsNumber = parseFloat(cleaned);

    // Si valeur numérique valide
    if (!isNaN(valueAsNumber)) {
      if (valueAsNumber > MAX_AMOUNT) {
        this.errorService.showError(
          '💸 Pauline, tu as encore tenté un coup de folie ? Sérieusement ? <br> C’est une liste de cadeaux, <em>pas un prêt immobilier pour un hôtel particulier dans le XVIe ! </em> <br> <br> La limite chez (Moments) est <strong>99 999 999 €</strong> ... et c\'est déjà pas mal !'
        );
        // Remet l’ancienne valeur
        const currentControl = this.giftForm.get(key);
        input.value = currentControl?.value?.toString() || '';
        return;
      }

      // ✅ Tout est bon, met à jour le champ proprement
      this.giftForm.get(key)?.setValue(valueAsNumber);
      input.value = valueAsNumber.toString(); // on synchronise l'affichage
    } else {
      // pas un nombre valide ? on laisse l’utilisateur corriger, mais on ne fait rien
      this.giftForm.get(key)?.setValue(undefined);
    }
  }


}
