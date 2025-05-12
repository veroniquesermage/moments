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
  errorMessage: string | null = null;
  message = '';
  modalActions:  TerminalModalAction[] = [];


  constructor(public giftService: GiftService,
              public router: Router,
              public authService: AuthService) {
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
    await this.giftService.deleteGift(this.gift.id!);
    await this.router.navigate(['/dashboard/mes-cadeaux']);
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
      this.message = 'Désolé, une erreur est survenue, veuillez réessayer plus tard.';
    } else if (!result.data.ok) {
      this.message = 'Aïe ! Il semble que quelqu\'un ait été plus rapide que vous.\nCe cadeau n\'est plus disponible';
    }

    if (!result.success || !result.data.ok) {
      this.modalActions= [
        { label: 'Ok', eventName: 'CANCEL', style: 'danger' }
      ] as TerminalModalAction[];
    } else {
      this.message = messageConfirmation;
      this.modalActions = [
        { label: 'Oui', eventName: eventName, style: 'primary' },
        { label: 'Non', eventName: 'CANCEL', style: 'secondary' }
      ] as TerminalModalAction[];
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
      // Redirige vers la liste des cadeaux
      this.router.navigate(['/dashboard/leurs-cadeaux']);
    } else {
      console.log('Oups comething went wrong', result.data);
      this.errorMessage = result.message!;
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
    }
    this.showModal = false;
  }
}
