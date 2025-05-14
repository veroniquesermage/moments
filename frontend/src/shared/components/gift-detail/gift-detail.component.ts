import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Gift} from 'src/core/models/gift.model';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {AuthService} from 'src/security/service/auth.service';
import {GiftAction} from 'src/core/enum/gift-action.enum';
import {GiftStatutDTO} from 'src/core/models/gift-statut.model';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';
import {ErrorService} from 'src/core/services/error.service';

@Component({
  selector: 'app-gift-detail',
  standalone: true,
  imports: [CommonModule, TerminalModalComponent],
  templateUrl: './gift-detail.component.html',
  styleUrl: './gift-detail.component.scss'
})
export class GiftDetailComponent implements OnInit {

  @Input() id!: number;
  @Input() context: 'own' | 'other' = 'own';
  @Output() back = new EventEmitter<void>();
  gift: Gift | undefined = undefined;
  showModal = false;
  pendingAction: 'RESERVER' | 'PRENDRE' | 'SUPPRIMER' | null = null;
  message = '';
  modalActions:  TerminalModalAction[] = [];


  constructor(public giftService: GiftService,
              public router: Router,
              public authService: AuthService,
              public errorService: ErrorService) {
  }

  async ngOnInit(): Promise<void> {
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.gift = result.data;
    }
  }

  modifier() {
    this.router.navigate(['/dashboard/mes-cadeaux/modifier', this.gift?.id]);
  }

  requestDelete() {
    this.message = 'Etes-vous sûr de vouloir supprimer ce cadeau ?';
    this.modalActions = [
      { label: 'Oui', eventName: 'DELETE', style: 'primary' },
      { label: 'Non', eventName: 'CANCEL', style: 'secondary' }
    ] as TerminalModalAction[];
    this.showModal = true;
  }

  async confirmDelete() {
    if (!this.gift) return;

    const result = await this.giftService.deleteGift(this.gift.id!);
    if (result.success) {
      await this.giftService.fetchGifts(); // tu appelles que si c’est réussi et seulement si le composant a besoin
      await this.router.navigate(['/dashboard/mes-cadeaux']);
    } else {
      this.errorService.showError(result.message);
    }
  }

  estReserveParMoi(gift: Gift): boolean {
    return gift.statut === 'RESERVE'
      && gift.reservePar?.id === this.authService.profile()?.id;
  }

  async reserver() {
    await this.verifierEtAfficherModal(GiftAction.RESERVER, 'Êtes-vous sûr de vouloir réserver ce cadeau pour 3 jours ?', 'RESERVER')
  }

  async prendre() {
    await this.verifierEtAfficherModal(GiftAction.PRENDRE, 'Êtes-vous sûr de vouloir prendre ce cadeau ?', 'PRENDRE')
  }

  private async verifierEtAfficherModal(action: GiftAction, messageConfirmation: string, eventName: string) {
    const result = await this.giftService.getEligibilityForGift(this.id, action);

    if (!result.success) {
      // Erreur réseau ou technique
      this.message = result.message ?? 'Désolé, une erreur est survenue, veuillez réessayer plus tard.';
      this.modalActions = [
        { label: 'Ok', eventName: 'CANCEL', style: 'danger' }
      ];
    } else if (!result.data.ok) {
      // Cas métier : pas éligible
      this.message = result.data.message ?? 'Ce cadeau n\'est plus disponible.';
      this.modalActions = [
        { label: 'Ok', eventName: 'CANCEL', style: 'danger' }
      ];
    } else {
      // Tout est ok : confirmation classique
      this.message = messageConfirmation;
      this.modalActions = [
        { label: 'Oui', eventName: eventName, style: 'primary' },
        { label: 'Non', eventName: 'CANCEL', style: 'secondary' }
      ];
      this.pendingAction = action;
    }
    this.showModal = true;
  }

  async confirmerStatut(status: GiftStatus) {
    const statut: GiftStatutDTO = {
      status: status
    };

    const result = await this.giftService.changerStatutGift(this.id, statut);

    if (result.success) {
      if(status === GiftStatus.RESERVE){
        this.message = 'Félicitation vous avez réservé le cadeau. Vous avez 3 jours pour confirmer l\'avoir pris. '
        this.modalActions= [
          { label: 'Ok', eventName: 'BACK_TO_LIST', style: 'primary' }
        ] as TerminalModalAction[];
      } else{
        this.message = 'Votre action est confirmée. <br>Vous pourrez <strong>ajouter date et lieu de livraison<\strong> et <strong>assurer le suivi<\strong> ou <strong>annuler<\strong> ce cadeau depuis le Suivi des cadeaux réservés/pris.'

        this.modalActions= [
          { label: 'Ok', eventName: 'BACK_TO_LIST', style: 'primary' },
          { label: 'Allez au suivi des cadeaux', eventName: 'SUIVI', style: 'primary' }
        ] as TerminalModalAction[];
      }
      this.showModal = true;
    } else {
      console.log('Oups comething went wrong', result.message);
      this.message = result.message ?? 'Désolé, une erreur est survenue, veuillez réessayer plus tard.';
      this.modalActions = [
        { label: 'Ok', eventName: 'CANCEL', style: 'danger' }
      ];
    }

  }

  handleClicked(eventName: string) {
    if(eventName === 'PRENDRE'){
      this.confirmerStatut(GiftStatus.PRIS);
    } else if (eventName === 'RESERVER'){
      this.confirmerStatut(GiftStatus.RESERVE);
    } else if(eventName === 'CANCEL'){
      this.pendingAction = null;
    } else if(eventName === 'DELETE'){
      this.confirmDelete();
    } else if(eventName=== 'SUIVI'){
      this.router.navigate(['/suivi']);
    } else if(eventName === 'BACK_TO_LIST'){
      this.router.navigate(['/dashboard/leurs-cadeaux']);
    }
    this.showModal = false;
  }
}
