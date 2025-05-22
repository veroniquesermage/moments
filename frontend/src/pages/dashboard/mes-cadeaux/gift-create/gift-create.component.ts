import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {Gift} from 'src/core/models/gift.model';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {AuthService} from 'src/security/service/auth.service';
import {GiftFormComponent} from 'src/shared/components/gift-form/gift-form.component';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';

@Component({
  selector: 'app-gift-create',
  standalone: true,
  imports: [CommonModule, GiftFormComponent, TerminalModalComponent],
  templateUrl: './gift-create.component.html',
  styleUrl: './gift-create.component.scss'
})
export class GiftCreateComponent {

  constructor(private giftService: GiftService,
              public router: Router,
              private authService: AuthService,
              public errorService: ErrorService) {
  }

  async onSubmit(giftFormData: Gift): Promise<void> {
    const giftslist = this.giftService.gifts();
    const utilisateur = this.authService.profile();
    const newPriority = Math.max(1, giftslist.length + 1);

    if (!utilisateur) {
      this.errorService.showError("❌ Impossible de créer un cadeau sans utilisateur connecté.");
      return;
    }

    const gift: Gift = {
      ...giftFormData,
      utilisateur: utilisateur,
      statut: GiftStatus.DISPONIBLE,
      recu: false,
      priorite: newPriority,
    };

    const result = await  this.giftService.createGift(gift);
    if (result.success) {
      await this.giftService.fetchGifts(); // tu appelles que si c’est réussi et seulement si le composant a besoin
      await this.router.navigate(['/dashboard/mes-cadeaux']);
    } else {
      this.errorService.showError(result.message);
    }
  }

}
