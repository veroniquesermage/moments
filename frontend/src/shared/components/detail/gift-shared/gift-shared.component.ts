import {Component, EventEmitter, Input, Output} from '@angular/core';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {GiftShared} from 'src/core/models/gift/gift_shared.model';
import {RoleUser} from 'src/core/enum/role-user.enum';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-gift-shared',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './gift-shared.component.html',
  styleUrl: './gift-shared.component.scss'
})
export class GiftSharedComponent {

  @Input()
  giftDetailResponse!: GiftDetailResponse;
  @Output() remboursementToggled = new EventEmitter<GiftShared>();
  partage = this.giftDetailResponse.partage

  get isPreneur(): boolean {
    return this.giftDetailResponse.droitsUtilisateur === RoleUser.PRENEUR;
  }


  toggleRemboursement(participantId: number) {
    const partageParticipant = this.partage?.find(p => p.participant.id === participantId);
    if (partageParticipant) {
      partageParticipant.rembourse = !partageParticipant.rembourse;
      this.remboursementToggled.emit(partageParticipant);
    }
  }

}
