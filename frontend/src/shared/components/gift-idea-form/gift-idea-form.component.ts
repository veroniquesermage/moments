import {Component, EventEmitter, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import {FormControl, FormGroup, FormsModule, ReactiveFormsModule, Validators} from '@angular/forms';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftIdeasResponse} from 'src/core/models/gift/gift-ideas-response.model';
import {CommonModule} from '@angular/common';
import {User} from 'src/security/model/user.model';
import {GiftIdeaFormData} from 'src/core/models/gift/idea-form-data.model';

@Component({
  selector: 'app-gift-idea-form',
  standalone: true,
  imports: [
    FormsModule,
    ReactiveFormsModule,
    CommonModule
  ],
  templateUrl: './gift-idea-form.component.html',
  styleUrl: './gift-idea-form.component.scss'
})
export class GiftIdeaFormComponent implements OnChanges {
  @Input() giftIdeasResponse: GiftIdeasResponse | undefined;
  @Input() membersGroup: User[] = [];

  @Output() formSubmitted = new EventEmitter<GiftIdeaFormData>();
  @Output() cancel = new EventEmitter<void>();

  giftForm: FormGroup = this.createGiftForm(undefined);

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['giftIdeasResponse']) {
      this.giftForm = this.createGiftForm(this.giftIdeasResponse?.gift);
    }
  }

  private createGiftForm(gift?: GiftPublicResponse): FormGroup {
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
      commentaire: new FormControl(gift?.commentaire ?? ''),
      destinataireId: new FormControl(gift?.destinataire.id ?? null, Validators.required)
    });
  }

  onSubmit(): void {
    console.log("📤 Form émis :", this.giftForm.value);

    if (this.giftForm.valid) {
      this.formSubmitted.emit(this.giftForm.value as GiftIdeaFormData);
    }
  }

  sanitizeDecimal(event: Event, key: string): void {
    const input = event.target as HTMLInputElement;
    input.value = input.value.replace(',', '.');
    this.giftForm.get(key)?.setValue(input.value);
  }

}
