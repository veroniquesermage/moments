import {Component, Input} from '@angular/core';
import {Gift} from 'src/core/models/gift/gift.model';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-gift-statut',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './gift-statut.component.html',
  styleUrl: './gift-statut.component.scss'
})
export class GiftStatutComponent {

  @Input()
  gift!: Gift;

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
