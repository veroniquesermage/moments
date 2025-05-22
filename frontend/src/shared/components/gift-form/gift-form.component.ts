import {Component, EventEmitter, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {Gift} from 'src/core/models/gift.model';
import {Router} from '@angular/router';

@Component({
  selector: 'app-gift-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './gift-form.component.html',
  styleUrl: './gift-form.component.scss'
})
export class GiftFormComponent implements OnChanges{

  giftForm: FormGroup;
  @Input() gift: Gift | undefined = undefined;
  @Output() formSubmitted = new EventEmitter<Gift>();
  @Output() cancel = new EventEmitter<void>();


  constructor(private fb: FormBuilder,
              public router: Router,) {
    this.giftForm = this.createGiftForm(this.gift);
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['gift'] && this.gift) {
      this.giftForm.patchValue(this.gift);
    }
  }

  onSubmit(): void {
    if (this.giftForm.valid) {
      this.formSubmitted.emit(this.giftForm.value as Gift);
    }
  }


  private createGiftForm(gift: Gift | undefined): FormGroup {
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

  sanitizeDecimal(event: Event, key: string ): void {
    const input = event.target as HTMLInputElement;
    input.value = input.value.replace(',', '.');
    // met à jour le FormControl manuellement
    this.giftForm.get(key)?.setValue(input.value);
  }

}
