import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Gift} from 'src/core/models/gift.model';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {AuthService} from 'src/security/service/auth.service';
import {GiftAction} from 'src/core/enum/gift-action.enum';

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
  mode: 'confirm' | 'error' = 'confirm';
  pendingAction: 'RESERVER' | 'PRENDRE' | 'SUPPRIMER' | null = null;
  message: string = 'Êtes-vous sûr(e) de vouloir supprimer ce cadeau ?';
  errorMessage: string | null = null;


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

  handleConfirm() {
    if (this.pendingAction === 'RESERVER') {
      this.confirmerReservation();
    } else if (this.pendingAction === 'PRENDRE') {
      this.confirmerPrise();
    } else if (this.pendingAction === 'SUPPRIMER') {
      this.confirmDelete();
    }

    this.pendingAction = null;
    this.showModal = false;
  }

  handleClose() {
    this.showModal = false;
  }

  handleCancel() {
    this.pendingAction = null;
    this.showModal = false;
  }


  async reserver() {
    const result = await this.giftService.getEligibilityForGift(this.id, GiftAction.RESERVER);
    if (!result.success) {
      this.mode = 'error';
      this.message = 'Désolé, une erreur est survenue, veuillez réessayer plus tard.';
    } else if (!result.data.ok) {
      this.mode = 'error';
      this.message = 'Aïe ! Il semble que quelqu\'un ait été plus rapide que vous.\nCe cadeau n\'est plus disponible à la réservation';
    } else {
      this.mode = 'confirm';
      this.message = 'Êtes-vous sûr de vouloir réserver ce cadeau pour 3 jours ?';
      this.pendingAction = 'RESERVER';
    }

    this.showModal = true;
  }

  async prendre() {
    const result = await this.giftService.getEligibilityForGift(this.id, GiftAction.PRENDRE);
    if (!result.success) {
      this.mode = 'error';
      this.message = 'Désolé, une erreur est survenue, veuillez réessayer plus tard.';
    } else if (!result.data.ok) {
      this.mode = 'error';
      this.message = 'Aïe ! Il semble que quelqu\'un ait été plus rapide que vous.\nCe cadeau n\'est plus disponible.';
    } else {
      this.mode = 'confirm';
      this.message = 'Êtes-vous sûr de vouloir prendre ce cadeau ?';
      this.pendingAction = 'PRENDRE';
    }

    this.showModal = true;
  }

  async confirmerReservation() {
    const result = await this.giftService.reserveGift(this.id);

    if (result.success) {
      // Redirige vers la liste des cadeaux
      this.router.navigate(['/dashboard/leurs-cadeaux']);
    } else {
      console.log('Oups comething went wrong', result.data);
      // this.errorMessage = result.message;
    }
  }

  private confirmerPrise() {
    this.router.navigate([`/dashboard/leurs-cadeaux/${this.id}/prendre`]);
  }
}
