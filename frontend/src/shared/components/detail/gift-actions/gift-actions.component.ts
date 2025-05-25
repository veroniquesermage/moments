import {Component, EventEmitter, Input, Output} from '@angular/core';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {RoleUser} from 'src/core/enum/role-user.enum';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {AuthService} from 'src/security/service/auth.service';
import {ErrorService} from 'src/core/services/error.service';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-gift-actions',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './gift-actions.component.html',
  styleUrl: './gift-actions.component.scss'
})
export class GiftActionsComponent {

  @Input() giftDetailResponse!: GiftDetailResponse;
  @Input() context!: 'mes-cadeaux' | 'cadeaux-groupe' | 'suivi' | 'idee-cadeau';

  @Output() editRequested = new EventEmitter<void>();
  @Output() deleteRequested = new EventEmitter<void>();
  @Output() reserveRequested = new EventEmitter<void>();
  @Output() takeRequested = new EventEmitter<void>();
  @Output() cancelReservationRequested = new EventEmitter<void>();
  @Output() withdrawRequested = new EventEmitter<void>();
  @Output() manageDeliveryRequested = new EventEmitter<void>();
  @Output() manageSharingRequested = new EventEmitter<void>();
  @Output() backRequested = new EventEmitter<void>();

  protected readonly RoleUser = RoleUser;
  protected readonly GiftStatus = GiftStatus;

  constructor(public giftService: GiftService,
              public router: Router,
              public authService: AuthService,
              public errorService: ErrorService) {
  }

  get role(): RoleUser {
    return this.giftDetailResponse.droitsUtilisateur;
  }

  get statut(): GiftStatus {
    return this.giftDetailResponse.gift.statut;
  }

  get reserveParMoi(): boolean {
    const currentUserId = this.giftDetailResponse.gift.reservePar?.id;
    const myId = this.authService.profile()?.id;
    return currentUserId === myId;
  }

  get canEdit(): boolean {
    return this.context === 'mes-cadeaux' && this.role === RoleUser.CREATEUR;
  }

  get canDelete(): boolean {
    return this.context === 'mes-cadeaux' && this.role === RoleUser.CREATEUR;
  }

  get canReserve(): boolean {
    return this.context === 'cadeaux-groupe' && this.statut === GiftStatus.DISPONIBLE;
  }

  get canTake(): boolean {
    return this.context === 'cadeaux-groupe' &&
      (this.statut === GiftStatus.DISPONIBLE ||
        (this.statut === GiftStatus.RESERVE && this.reserveParMoi));
  }

  get canCancelReservation(): boolean {
    return this.context === 'cadeaux-groupe' &&
      this.statut === GiftStatus.RESERVE &&
      this.reserveParMoi;
  }

  get canWithdraw(): boolean {
    return this.context === 'cadeaux-groupe' &&
      (this.statut === GiftStatus.PRIS || this.statut === GiftStatus.PARTAGE) &&
      this.reserveParMoi;
  }

  get canManageDelivery(): boolean {
    return this.context === 'suivi' && this.role === RoleUser.PRENEUR;
  }

  get canManageSharing(): boolean {
    return this.context === 'suivi' && this.role === RoleUser.PRENEUR;
  }

  get canGoBack(): boolean {
    return true;
  }

}
