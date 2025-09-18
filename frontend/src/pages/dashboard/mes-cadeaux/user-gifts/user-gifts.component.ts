import {Component, OnInit, signal} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {GiftPriorityListComponent} from 'src/shared/components/gift-priority-list/gift-priority-list.component';
import {GiftResponse} from 'src/core/models/gift/gift-response.model';
import {PaginationComponent} from 'src/shared/components/pagination/pagination.component';
import {PaginationInfo} from 'src/core/models/common/pagination.model';

@Component({
  selector: 'app-user-gifts',
  imports: [CommonModule, GiftPriorityListComponent,PaginationComponent],
  standalone: true,
  templateUrl: './user-gifts.component.html',
  styleUrl: './user-gifts.component.scss'
})
export class UserGiftsComponent implements OnInit{

  currentPage = signal(1);
  paginationInfo = signal<PaginationInfo | null>(null);
  gifts = signal<GiftResponse[]>([]);

  constructor(public giftService: GiftService,
              public router : Router) {
  }

  async ngOnInit(): Promise<void> {
    await this.loadGifts(1);
  }

  async loadGifts(page: number): Promise<void> {
    const result = await this.giftService.fetchGifts(undefined, page);

    if (result.success && result.data) {
      this.currentPage.set(page);
      this.paginationInfo.set(result.data.pagination);
      this.gifts.set(result.data.items);
    }
  }

  async onPageChange(page: number): Promise<void> {
    await this.loadGifts(page);
    // Scroll to top pour une meilleure UX
    window.scrollTo({ top: 0, behavior: 'smooth' });
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
