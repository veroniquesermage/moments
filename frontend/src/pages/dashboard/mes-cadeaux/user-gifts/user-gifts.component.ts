import {Component, OnInit, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {GiftPriorityListComponent} from 'src/shared/components/gift-priority-list/gift-priority-list.component';
import {GiftResponse} from 'src/core/models/gift/gift-response.model';

@Component({
  selector: 'app-user-gifts',
  imports: [CommonModule, GiftPriorityListComponent],
  standalone: true,
  templateUrl: './user-gifts.component.html',
  styleUrl: './user-gifts.component.scss'
})
export class UserGiftsComponent implements OnInit{

  gifts = signal<GiftResponse[]>([]);

  constructor(public giftService: GiftService,
              public router : Router) {
  }

  async ngOnInit(): Promise<void> {
    await this.loadGifts();
  }

  async loadGifts(): Promise<void> {
    // Charger tous les cadeaux en utilisant la limite maximale du backend (100)
    const MAX_LIMIT = 100;
    const allGifts: GiftResponse[] = [];
    let currentPage = 1;
    let hasMorePages = true;

    while (hasMorePages) {
      const result = await this.giftService.fetchGifts(undefined, currentPage, MAX_LIMIT);

      if (result.success && result.data) {
        allGifts.push(...result.data.items);
        hasMorePages = result.data.pagination.has_next;
        currentPage++;
      } else {
        hasMorePages = false;
      }
    }

    this.gifts.set(allGifts);
  }

  goToAjout(): void {
    void this.router.navigate(['/dashboard/mes-cadeaux/creer']);
  }

  onGiftClicked(gift: GiftResponse): void {
    void this.router.navigate(['/dashboard/cadeau', gift.id], {
      queryParams: { context: 'mes-cadeaux' }
    });
  }

  return() {
    void this.router.navigate(['/dashboard']);
  }
}
