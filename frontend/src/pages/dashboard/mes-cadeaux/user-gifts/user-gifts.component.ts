import {Component, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {Gift} from 'src/core/models/gift/gift.model';
import {GiftPriorityListComponent} from 'src/shared/components/gift-priority-list/gift-priority-list.component';

@Component({
  selector: 'app-user-gifts',
  imports: [CommonModule, GiftPriorityListComponent],
  standalone: true,
  templateUrl: './user-gifts.component.html',
  styleUrl: './user-gifts.component.scss'
})
export class UserGiftsComponent implements OnInit{



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

  return() {
    this.router.navigate(['/dashboard']);
  }
}
