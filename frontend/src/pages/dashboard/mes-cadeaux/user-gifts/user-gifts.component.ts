import {Component, OnInit} from '@angular/core';
import {GiftTableComponent} from 'src/shared/components/gift-table/gift-table.component';
import {CommonModule} from '@angular/common';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {Gift} from 'src/core/models/gift/gift.model';

@Component({
  selector: 'app-user-gifts',
  imports: [CommonModule, GiftTableComponent],
  standalone: true,
  templateUrl: './user-gifts.component.html',
  styleUrl: './user-gifts.component.scss'
})
export class UserGiftsComponent implements OnInit{

  displayedColumns = [
    { key: 'nom', label: 'Nom' },
    { key: 'prix', label: 'Prix (€)', formatFn: (v: number | null) => v != null ? `${v}€` : '—'},
    { key: 'priorite', label: 'Priorité' }
  ];

  constructor(public giftService: GiftService,
              public router : Router) {
  }

  ngOnInit(): void {
    this.giftService.fetchGifts();
  }

  goToAjout(): void {
    this.router.navigate(['/dashboard/mes-cadeaux/creer']);
  }

  onGiftClicked(gift: Gift): void {
    this.router.navigate(['/dashboard/cadeau', gift.id], {
      queryParams: { context: 'mes-cadeaux' }
    });
  }

  retour() {
    this.router.navigate(['/dashboard']);
  }
}
