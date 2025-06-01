import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {AuthService} from 'src/security/service/auth.service';
import {GiftFormComponent} from 'src/shared/components/gift-form/gift-form.component';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GiftResponse} from 'src/core/models/gift/gift-response.model';
import {GiftCreate} from 'src/core/models/gift/gift-create.model';

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

  async onSubmit(giftFormData: GiftResponse): Promise<void> {
    const giftslist = this.giftService.giftsResponse();
    const destinataire = this.authService.profile();
    const newPriority = Math.max(1, giftslist.length + 1);

    if (!destinataire) {
      this.errorService.showError("❌ Impossible de créer un cadeau sans utilisateur connecté.");
      return;
    }

    const giftCreate: GiftCreate = {
      destinataireId: destinataire.id,
      nom: giftFormData.nom,
      description: giftFormData.description,
      marque: giftFormData.marque,
      magasin: giftFormData.magasin,
      url: giftFormData.url,
      quantite: giftFormData.quantite,
      prix: giftFormData.prix,
      fraisPort: giftFormData.fraisPort,
      commentaire: giftFormData.commentaire,
      priorite: newPriority,
      statut: GiftStatus.DISPONIBLE,
    };

    const result = await  this.giftService.createGift(giftCreate);
    if (result.success) {
      await this.giftService.fetchGifts(); // tu appelles que si c’est réussi et seulement si le composant a besoin
      await this.router.navigate(['/dashboard/mes-cadeaux']);
    } else {
      this.errorService.showError(result.message);
    }
  }

}
