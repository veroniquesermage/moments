import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {AuthService} from 'src/security/service/auth.service';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';
import {ErrorService} from 'src/core/services/error.service';
import {GiftHeaderComponent} from 'src/shared/components/detail/gift-header/gift-header.component';
import {GiftDeliveryComponent} from 'src/shared/components/detail/gift-delivery/gift-delivery.component';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {RoleUser} from 'src/core/enum/role-user.enum';
import {GiftSharedComponent} from 'src/shared/components/detail/gift-shared/gift-shared.component';
import {GiftShared} from 'src/core/models/gift/gift_shared.model';
import {GiftActionsComponent} from 'src/shared/components/detail/gift-actions/gift-actions.component';
import {GiftAction} from 'src/core/enum/gift-action.enum';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {SharingService} from 'src/core/services/sharing.service';

@Component({
  selector: 'app-gift-detail',
  standalone: true,
  imports: [CommonModule, TerminalModalComponent, GiftHeaderComponent, GiftDeliveryComponent, GiftSharedComponent, GiftActionsComponent],
  templateUrl: './gift-detail.component.html',
  styleUrl: './gift-detail.component.scss'
})
export class GiftDetailComponent implements OnInit{

  @Input() id!: number;
  @Input() context: 'mes-cadeaux' | 'cadeaux-groupe' | 'suivi' | 'idee-cadeau' = 'mes-cadeaux';
  @Output() back = new EventEmitter<void>();
  giftDetail!: GiftDetailResponse;
  showModal = false;
  pendingAction: GiftAction | undefined;
  message = '';
  modalActions:  TerminalModalAction[] = [];
  currentUserId: number |undefined;
  protected readonly RoleUser = RoleUser;

  constructor(public giftService: GiftService,
              public sharingService: SharingService,
              public router: Router,
              public authService: AuthService,
              public errorService: ErrorService) {
  }

  async ngOnInit(): Promise<void> {
    this.currentUserId = this.authService.profile()?.id;
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.giftDetail = result.data;
      console.log(this.giftDetail.droitsUtilisateur)
    } else {
      this.errorService.showError(result.message);
    }
  }

  async onReceptionToggled(newValue: boolean) {
    const result = await this.giftService.setGiftReceived(this.id, newValue);
    if (result.success) {
      this.giftDetail = result.data; // met à jour localement
    } else {
      this.errorService.showError(result.message);
    }
  }

  async onRemboursementToggled(newValue: GiftShared) {
    const result = await this.sharingService.setGiftRefunded(newValue);
    if (result.success) {
      this.giftDetail = result.data; // met à jour localement
    } else {
      this.errorService.showError(result.message);
    }
  }

  modifier(): void {
    this.router.navigate(['/dashboard/mes-cadeaux/modifier', this.giftDetail.gift.id]);
  }

  gererLivraison(): void {
    this.router.navigate(['/dashboard/cadeaux-suivis/livraison', this.giftDetail.gift.id]);
  }

  gererPartage(): void {
    this.router.navigate(['/dashboard/partage', this.giftDetail.gift.id], {
      queryParams: { context: 'suivi' }
    });
  }

  retour(): void {
    if (this.context === 'mes-cadeaux') {
      this.router.navigate(['/dashboard/mes-cadeaux']);
    } else if (this.context === 'cadeaux-groupe') {
      this.router.navigate(['/dashboard/leurs-cadeaux']);
    } else if (this.context === 'suivi') {
      this.router.navigate(['/dashboard/cadeaux-suivis']);
    } else {
      this.router.navigate(['/dashboard']);
    }
  }

  requestDelete(): void {
    this.message = 'Êtes-vous sûr de vouloir supprimer ce cadeau ?';
    this.modalActions = [
      { label: 'Oui', eventName: 'DELETE', style: 'primary' },
      { label: 'Non', eventName: 'CANCEL', style: 'secondary' }
    ];
    this.showModal = true;
  }

  async confirmDelete(): Promise<void> {
    const result = await this.giftService.deleteGift(this.id);

    if (result.success) {
      await this.router.navigate(['/dashboard/mes-cadeaux']);
    } else {
      this.errorService.showError(result.message);
    }
  }

  handleClicked(eventName: string): void {
    if (eventName === 'DELETE') {
      this.confirmDelete();
    } else if (eventName === 'RESERVER') {
      this.confirmerStatut(GiftStatus.RESERVE);
    } else if (eventName === 'PRENDRE') {
      this.confirmerStatut(GiftStatus.PRIS);
    } else if (eventName === 'ANNULER_RESERVATION' || eventName === 'RETIRER') {
      this.confirmerStatut(GiftStatus.DISPONIBLE);
    } else if (eventName === 'CANCEL') {
      this.pendingAction = undefined;
      this.showModal = false;
    } else if (eventName === 'PARTAGE') {
      this.router.navigate(['/dashboard/partage', this.giftDetail.gift.id], {
        queryParams: { context: 'cadeaux-groupe' }
      });
    } else if (eventName === 'BACK_TO_LIST') {
      this.retour();
    }
  }

  reserver(): void {
    this.verifierEtAfficherModal(
      GiftAction.RESERVER,
      'Êtes-vous sûr de vouloir réserver ce cadeau pour 3 jours ?',
      'RESERVER'
    );
  }

  prendre(): void {
    this.verifierEtAfficherModal(
      GiftAction.PRENDRE,
      'Êtes-vous sûr de vouloir prendre ce cadeau ?',
      'PRENDRE'
    );
  }

  async verifierEtAfficherModal(action: GiftAction, messageConfirmation: string, eventName: string): Promise<void> {
    const result = await this.giftService.getEligibilityForGift(this.id, action);

    if (!result.success) {
      this.message = result.message ?? 'Désolé, une erreur est survenue, veuillez réessayer plus tard.';
      this.modalActions = [
        { label: 'Ok', eventName: 'CANCEL', style: 'danger' }
      ];
    } else if (!result.data.ok) {
      this.message = result.data.message ?? 'Ce cadeau n\'est plus disponible.';
      this.modalActions = [
        { label: 'Ok', eventName: 'CANCEL', style: 'danger' }
      ];
    } else {
      this.message = messageConfirmation;
      this.modalActions = [
        { label: 'Oui', eventName, style: 'primary' },
        { label: 'Non', eventName: 'CANCEL', style: 'secondary' }
      ];
      this.pendingAction = action;
    }

    this.showModal = true;
  }

  async confirmerStatut(status: GiftStatus): Promise<void> {
    const result = await this.giftService.changeStatusGift(this.id, { status });

    if (result.success) {
      if (status === GiftStatus.RESERVE) {
        this.message = 'Félicitations, vous avez réservé le cadeau. Vous avez 3 jours pour le confirmer.';
        this.modalActions = [
          { label: 'Ok', eventName: 'BACK_TO_LIST', style: 'primary' }
        ];
      } else {
        this.message = 'Votre action est confirmée. Souhaitez-vous le partager avec d\'autres membres du groupe ?';
        this.modalActions = [
          { label: 'Ok', eventName: 'BACK_TO_LIST', style: 'primary' },
          { label: 'Partager le cadeau', eventName: 'PARTAGE', style: 'primary' }
        ];
      }

      this.showModal = true;
    } else {
      this.message = result.message ?? 'Une erreur est survenue.';
      this.modalActions = [
        { label: 'Ok', eventName: 'CANCEL', style: 'danger' }
      ];
      this.showModal = true;
    }
  }

  annulerReservation(): void {
    this.verifierEtAfficherModal(
      GiftAction.ANNULER_RESERVATION,
      'Souhaitez-vous annuler votre réservation ? Le cadeau redeviendra disponible pour les autres membres.',
      'ANNULER_RESERVATION'
    );
  }

  retirerCadeau(): void {
    this.verifierEtAfficherModal(
      GiftAction.RETIRER,
      'Souhaitez-vous retirer ce cadeau ? Il redeviendra disponible pour les autres membres.',
      'RETIRER'
    );
  }




}
