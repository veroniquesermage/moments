import {Component, EventEmitter, Input, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {CdkDragDrop, DragDropModule, moveItemInArray} from '@angular/cdk/drag-drop';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {GiftPriority} from 'src/core/models/gift/gift-priority.model';
import {UserInteractionService} from 'src/core/services/user-interaction.service';
import {GiftResponse} from 'src/core/models/gift/gift-response.model';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {FormatMontantPipe} from 'src/core/pipes/format-montant.pipe';

@Component({
  selector: 'app-gift-priority-list',
  standalone: true,
  imports: [
    CommonModule,
    DragDropModule,
    TerminalModalComponent,
    FormatMontantPipe
  ],
  templateUrl: './gift-priority-list.component.html',
  styleUrl: './gift-priority-list.component.scss'
})
export class GiftPriorityListComponent {
  @Input() gifts: GiftResponse[] = [];
  @Output() rowClicked = new EventEmitter<GiftResponse>();

  hasOrderChanged: boolean = false;

  constructor(private giftService: GiftService,
              public errorService: ErrorService,
              private userInteractionService: UserInteractionService) {
  }

  get userIsTabbing$() {
    return this.userInteractionService.isTabbing$;
  }

  onRowClick(gift: GiftResponse) {
    this.rowClicked.emit(gift);
  }

  drop(event: CdkDragDrop<GiftResponse[]>) {
    moveItemInArray(this.gifts, event.previousIndex, event.currentIndex);
    this.hasOrderChanged = true;
  }

  async recPriorities() {
    this.gifts.forEach((gift, index) => {
      gift.priorite = index + 1;
    });
    const giftPriority: GiftPriority[] = this.gifts.map(gift => (
      {
        id: gift.id!,
        priority: gift.priorite
      }
    ));
    const result = await this.giftService.updateAllGifts(giftPriority);
    if(result.success){
      this.hasOrderChanged = false;
    } else {
      this.errorService.showError("❌ Une erreur est survenue à l'enregistrement.")
    }
  }

  changeOrder(index: number, direction: 'up' | 'down') {
    const targetIndex = direction === 'up' ? index - 1 : index + 1;

    if (targetIndex < 0 || targetIndex >= this.gifts.length) return;

    moveItemInArray(this.gifts, index, targetIndex);
    this.hasOrderChanged = true;
  }

}
