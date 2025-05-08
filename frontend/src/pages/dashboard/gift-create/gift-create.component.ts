import {Component, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, FormControl, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {Gift} from 'src/core/models/gift.model';
import {User} from 'src/security/model/user.model';
import {GiftStatus} from 'src/core/enum/gift-status-.enum';
import {AuthService} from 'src/security/service/auth.service';

@Component({
  selector: 'app-gift-create',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './gift-create.component.html',
  styleUrl: './gift-create.component.scss'
})
export class GiftCreateComponent {
  giftForm: FormGroup;
  errorMessage: string | null = null;

  constructor(private fb: FormBuilder,
              private giftService: GiftService,
              public router: Router,
              private authService: AuthService,) {
    this.giftForm = this.createGiftForm();
  }

  async onSubmit() {

    const giftslist = this.giftService.gifts();
    const utilisateur = this.authService.profile();
    const newPriority = Math.max(1, giftslist.length + 1);

    if (!utilisateur) {
      this.giftService.errorMessage.set("❌ Impossible de créer un cadeau sans utilisateur connecté.");
      return;
    }

    if (this.giftForm.valid) {
      const formData = this.giftForm.value;
      console.log('🧾 Données du formulaire :', formData);

      let prix = formData.prix;
      if (typeof prix === 'string') {
        prix = Number(prix.replace(',', '.'));
      }


      const gift: Gift = {
        nom: formData.nom,
        description: formData.description,
        url: formData.url,
        quantite: formData.quantite,
        prix: prix,
        commentaire: formData.commentaire,
        utilisateurId: utilisateur.id,
        statut: GiftStatus.DISPONIBLE,
        recu: false,
        priorite: newPriority
      };

      await this.giftService.createGift(gift);
      await this.router.navigate(['/dashboard/mes-cadeaux']);

    }
  }

  private createGiftForm(): FormGroup {
    return new FormGroup({
      nom: new FormControl('', Validators.required),
      description: new FormControl(''),
      url: new FormControl(''),
      quantite: new FormControl('', Validators.required),
      prix: new FormControl(''),
      commentaire: new FormControl('')
    });
  }


}
