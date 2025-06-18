import {Component, EventEmitter, Input, Output} from '@angular/core';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {GiftShared} from 'src/core/models/gift/gift-shared.model';
import {RoleUser} from 'src/core/enum/role-user.enum';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {CommonModule} from '@angular/common';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';

@Component({
  selector: 'app-gift-shared',
  standalone: true,
  imports: [
    CommonModule,
    DisplayNamePipe
  ],
  templateUrl: './gift-shared.component.html',
  styleUrl: './gift-shared.component.scss'
})
export class GiftSharedComponent {

  @Input()
  giftDetailResponse!: GiftDetailResponse;
  @Input()
  context: 'mes-cadeaux' | 'cadeaux-groupe' | 'suivi' | 'idee-cadeau' = 'suivi';
  @Input()
  currentUserId!: number | undefined;
  @Output() remboursementToggled = new EventEmitter<GiftShared>();

  get partage(): GiftShared[] | undefined {
    return this.giftDetailResponse?.partage;
  }

  get isPreneur(): boolean {
    return this.giftDetailResponse.droitsUtilisateur === RoleUser.PRENEUR;
  }

  get isParticipant():boolean{
    return this.giftDetailResponse.droitsUtilisateur === RoleUser.PARTICIPANT;
  }

  toggleRemboursement(participantId: number) {
    const partageParticipant = this.partage?.find(p => p.participant.id === participantId);
    if (partageParticipant) {
      partageParticipant.rembourse = !partageParticipant.rembourse;
      this.remboursementToggled.emit(partageParticipant);
    }
  }

  getEmojiStatut(statut: GiftStatus): string {
    switch (statut) {
      case 'DISPONIBLE':
        return '🟢';
      case 'RESERVE':
        return '🟡';
      case 'PRIS':
        return '🔴';
      case 'PARTAGE':
        return '🟣';
      default:
        return '❓';
    }
  }

  getLabelPreneur(statut: GiftStatus): string {
    switch (statut) {
      case 'RESERVE': return 'Réservé par';
      case 'PRIS':
      case 'PARTAGE': return 'Pris par';
      default: return '';
    }
  }



  protected readonly GiftStatus = GiftStatus;

}
