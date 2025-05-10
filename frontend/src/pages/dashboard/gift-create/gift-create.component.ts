import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {Gift} from 'src/core/models/gift.model';
import {GiftStatus} from 'src/core/enum/gift-status-.enum';
import {AuthService} from 'src/security/service/auth.service';
import {GiftFormComponent} from 'src/shared/components/gift-form/gift-form.component';

@Component({
  selector: 'app-gift-create',
  standalone: true,
  imports: [CommonModule, GiftFormComponent],
  templateUrl: './gift-create.component.html',
  styleUrl: './gift-create.component.scss'
})
export class GiftCreateComponent {
  errorMessage: string | null = null;

  constructor(private giftService: GiftService,
              public router: Router,
              private authService: AuthService,) {
  }

  async onSubmit(giftFormData: Gift): Promise<void> {
    const giftslist = this.giftService.gifts();
    const utilisateur = this.authService.profile();
    const newPriority = Math.max(1, giftslist.length + 1);

    if (!utilisateur) {
      this.giftService.errorMessage.set("❌ Impossible de créer un cadeau sans utilisateur connecté.");
      return;
    }

    const gift: Gift = {
      ...giftFormData,
      utilisateurId: utilisateur.id,
      statut: GiftStatus.DISPONIBLE,
      recu: false,
      priorite: newPriority,
    };

    await this.giftService.createGift(gift);
    await this.router.navigate(['/dashboard/mes-cadeaux']);
  }

}
