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
import {GiftShared} from 'src/core/models/gift/gift-shared.model';
import {GiftActionsComponent} from 'src/shared/components/detail/gift-actions/gift-actions.component';
import {GiftAction} from 'src/core/enum/gift-action.enum';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {SharingService} from 'src/core/services/sharing.service';
import {GiftIdeaComponent} from 'src/shared/components/detail/gift-idea/gift-idea.component';
import {IdeaService} from 'src/core/services/idea.service';
import {ModalActionType} from 'src/core/enum/modal-action.enum';
import {format} from 'date-fns';
import {fr} from 'date-fns/locale';

@Component({
  selector: 'app-gift-detail',
  standalone: true,
  imports: [CommonModule, TerminalModalComponent, GiftHeaderComponent, GiftDeliveryComponent, GiftSharedComponent, GiftActionsComponent, GiftIdeaComponent],
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
              public ideaService: IdeaService,
              public sharingService: SharingService,
              public router: Router,
              public authService: AuthService,
              public errorService: ErrorService) {
  }

  async ngOnInit(): Promise<void> {
    this.currentUserId = this.authService.profile()?.id;
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      console.log("Gift detail :", result.data);
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
    void this.router.navigate(['/dashboard/mes-cadeaux/modifier', this.giftDetail.gift.id]);
  }

  modifierIdee():void {
    void this.router.navigate(['/dashboard/idees/modifier', this.giftDetail.gift.id]);
  }

  gererLivraison(): void {
    void this.router.navigate(['/dashboard/cadeaux-suivis/livraison', this.giftDetail.gift.id]);
  }

  gererPartage(): void {
    void this.router.navigate(['/dashboard/partage', this.giftDetail.gift.id], {
      queryParams: { context: 'suivi' }
    });
  }

  retour(): void {
    if (this.context === 'mes-cadeaux') {
      void this.router.navigate(['/dashboard/mes-cadeaux']);
    } else if (this.context === 'cadeaux-groupe') {
      void this.router.navigate(['/dashboard/leurs-cadeaux']);
    } else if (this.context === 'suivi') {
      void this.router.navigate(['/dashboard/cadeaux-suivis']);
    } else if (this.context === 'idee-cadeau') {
      void this.router.navigate(['/dashboard/idees']);
    } else {
      void this.router.navigate(['/dashboard']);
    }
  }

  requestDelete(): void {
    this.message = 'Êtes-vous sûr de vouloir supprimer ce cadeau ?';
    this.modalActions = [
      { label: 'Oui', eventName: ModalActionType.DELETE, style: 'primary' },
      { label: 'Non', eventName: ModalActionType.CANCEL, style: 'secondary' }
    ];
    this.showModal = true;
  }

  deleteIdea(): void{
    this.message = 'Êtes-vous sûr de vouloir supprimer cette idée de cadeau ?'
    this.modalActions = [
      { label: 'Oui', eventName: ModalActionType.DELETE_IDEA, style: 'primary' },
      { label: 'Non', eventName: ModalActionType.CANCEL, style: 'secondary' }
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

  async confirmDeleteIdea(): Promise<void> {
    const ideaId = this.giftDetail.ideas?.id;
    if(!ideaId){
      this.errorService.showError('Aucune idée associée à ce cadeau');
    }
    const result = await this.ideaService.deleteIdea(ideaId!);

    if (result.success) {
      await this.router.navigate(['/dashboard/idees']);
    } else {
      this.errorService.showError(result.message);
    }
  }

  handleClicked(eventName: string): void {
    if (eventName === ModalActionType.DELETE) {
      this.confirmDelete();
    } else if (eventName === ModalActionType.DELETE_IDEA) {
      this.confirmDeleteIdea();
    } else if (eventName === ModalActionType.RESERVER) {
      this.confirmerStatut(GiftStatus.RESERVE);
    } else if (eventName === ModalActionType.PRENDRE) {
      this.confirmerStatut(GiftStatus.PRIS);
    } else if (eventName === ModalActionType.ANNULER_RESERVATION || eventName === ModalActionType.RETIRER) {
      this.confirmerStatut(GiftStatus.DISPONIBLE);
    } else if (eventName === ModalActionType.CANCEL) {
      this.pendingAction = undefined;
      this.showModal = false;
    } else if (eventName === ModalActionType.PARTAGE) {
      void this.router.navigate(['/dashboard/partage', this.giftDetail.gift.id], {
        queryParams: { context: 'cadeaux-groupe' }
      });
    } else if (eventName === ModalActionType.BACK_TO_LIST) {
      this.retour();
    }
  }

  reserver(): void {
    const date = this.calculateReservationExpirationAndFormat();
    const message = `Êtes-vous sûr de vouloir réserver ce cadeau ?</br> </br> Si vous ne le prenez pas avant le <strong>${date}</strong>, il redeviendra disponible pour tous`;
    this.verifierEtAfficherModal(
      GiftAction.RESERVER,
      message,
      ModalActionType.RESERVER
    );
  }

  prendre(): void {
    this.verifierEtAfficherModal(
      GiftAction.PRENDRE,
      'Êtes-vous sûr de vouloir prendre ce cadeau ?',
      ModalActionType.PRENDRE
    );
  }

  async verifierEtAfficherModal(action: GiftAction, messageConfirmation: string, eventName: string): Promise<void> {
    const result = await this.giftService.getEligibilityForGift(this.id, action);

    if (!result.success) {
      this.message = result.message ?? 'Désolé, une erreur est survenue, veuillez réessayer plus tard.';
      this.modalActions = [
        { label: 'Ok', eventName: ModalActionType.CANCEL, style: 'danger' }
      ];
    } else if (!result.data.ok) {
      this.message = result.data.message ?? 'Ce cadeau n\'est plus disponible.';
      this.modalActions = [
        { label: 'Ok', eventName: ModalActionType.CANCEL, style: 'danger' }
      ];
    } else {
      this.message = messageConfirmation;
      this.modalActions = [
        { label: 'Oui', eventName, style: 'primary' },
        { label: 'Non', eventName: ModalActionType.CANCEL, style: 'secondary' }
      ];
      this.pendingAction = action;
    }

    this.showModal = true;
  }

  async confirmerStatut(status: GiftStatus): Promise<void> {
    const result = await this.giftService.changeStatusGift(this.id, { status });

    if (result.success) {
      if (status === GiftStatus.RESERVE) {
        const dateExpiration = this.calculateReservationExpirationAndFormat();
        this.message = `Félicitations, vous avez réservé le cadeau.</br> N'oubliez pas de le confirmer avant le <strong>${dateExpiration}</strong>.`;
        this.modalActions = [
          { label: 'Ok', eventName: ModalActionType.BACK_TO_LIST, style: 'primary' }
        ];
      } else if (status === GiftStatus.DISPONIBLE) {
        this.message = 'Votre action est confirmée.';
        this.modalActions = [
          { label: 'Ok', eventName: ModalActionType.BACK_TO_LIST, style: 'primary' }
        ];
      } else {
        this.message = 'Votre action est confirmée.</br> Souhaitez-vous le partager avec d\'autres membres du groupe ?';
        this.modalActions = [
          { label: 'Non', eventName: ModalActionType.BACK_TO_LIST, style: 'primary' },
          { label: 'Partager le cadeau', eventName: ModalActionType.PARTAGE, style: 'primary' }
        ];
      }

      this.showModal = true;
    } else {
      this.message = result.message ?? 'Une erreur est survenue.';
      this.modalActions = [
        { label: 'Ok', eventName: ModalActionType.CANCEL, style: 'danger' }
      ];
      this.showModal = true;
    }
  }

  annulerReservation(): void {
    this.verifierEtAfficherModal(
      GiftAction.ANNULER_RESERVATION,
      'Souhaitez-vous annuler votre réservation ?</br> Le cadeau redeviendra disponible pour les autres membres.',
      ModalActionType.ANNULER_RESERVATION
    );
  }

  retirerCadeau(): void {
    this.verifierEtAfficherModal(
      GiftAction.RETIRER,
      'Souhaitez-vous retirer ce cadeau ?</br> Il redeviendra disponible pour les autres membres.',
      ModalActionType.RETIRER
    );
  }

  calculateReservationExpirationAndFormat(): string {
    const expirationDate = new Date();

    // On ajoute 4 jours à la date
    expirationDate.setDate(expirationDate.getDate() + 4);

    // On fixe l’heure à 01h00
    expirationDate.setHours(1, 0, 0, 0);
    return format(expirationDate, "d MMMM 'à' HH'h'", {locale: fr});
  }



}
