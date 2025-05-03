import {Component, Input} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Gift} from 'src/core/models/gift.model';

@Component({
  selector: 'app-gift-table',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './gift-table.component.html',
  styleUrl: './gift-table.component.scss'
})
export class GiftTableComponent {
  @Input() gifts: Gift[] = [];
  @Input() displayedColumns: string[] = []; // Liste des colonnes dynamiques
}
