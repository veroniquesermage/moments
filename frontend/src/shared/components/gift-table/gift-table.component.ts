import {Component, EventEmitter, Input, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Gift} from 'src/core/models/gift.model';
import {GiftTableColumn} from 'src/core/models/gift-table-column.model';

@Component({
  selector: 'app-gift-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './gift-table.component.html',
  styleUrl: './gift-table.component.scss'
})
export class GiftTableComponent {
  @Input() gifts: Gift[] = [];
  @Input() displayedColumns: GiftTableColumn[] = [];
  @Output() rowClicked = new EventEmitter<Gift>();

  getGiftValue(gift: Gift, column: GiftTableColumn): any {
    const rawValue = (gift as any)[column.key];
    return column.formatFn ? column.formatFn(rawValue, gift) : rawValue;
  }

  onRowClick(gift: Gift) {
    this.rowClicked.emit(gift);
  }

}
