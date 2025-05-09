import {Component, EventEmitter, Input, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {Gift} from 'src/core/models/gift.model';

@Component({
  selector: 'app-gift-form',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './gift-form.component.html',
  styleUrl: './gift-form.component.scss'
})
export class GiftFormComponent {

  giftForm: FormGroup;
  @Input() gift: Gift | undefined = undefined;

  @Output() formSubmitted = new EventEmitter<Gift>();


  constructor(private fb: FormBuilder) {
    this.giftForm = this.createGiftForm(this.gift);
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
      description: new FormControl(gift?.description ?? ''),
      url: new FormControl(gift?.url ?? ''),
      quantite: new FormControl(gift?.quantite ?? 1, Validators.required),
      prix: new FormControl(gift?.prix ?? 0),
      commentaire: new FormControl(gift?.commentaire ?? '')
    });
  }

  sanitizeDecimal(event: Event): void {
    const input = event.target as HTMLInputElement;
    input.value = input.value.replace(',', '.');
    // met à jour le FormControl manuellement
    this.giftForm.get('prix')?.setValue(input.value);
  }

}
