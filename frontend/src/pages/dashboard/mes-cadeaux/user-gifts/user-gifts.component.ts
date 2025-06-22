import {Component, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {GiftPriorityListComponent} from 'src/shared/components/gift-priority-list/gift-priority-list.component';
import {GiftResponse} from 'src/core/models/gift/gift-response.model';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';

@Component({
  selector: 'app-user-gifts',
  imports: [CommonModule, GiftPriorityListComponent, FeedbackTestComponent],
  standalone: true,
  templateUrl: './user-gifts.component.html',
  styleUrl: './user-gifts.component.scss'
})
export class UserGiftsComponent implements OnInit{

  composant: string = "UserGiftsComponent";

  constructor(public giftService: GiftService,
              public router : Router) {
  }

  ngOnInit(): void {
    this.giftService.fetchGifts();
  }

  goToAjout(): void {
    this.router.navigate(['/dashboard/mes-cadeaux/creer']);
  }

  onGiftClicked(gift: GiftResponse): void {
    this.router.navigate(['/dashboard/cadeau', gift.id], {
      queryParams: { context: 'mes-cadeaux' }
    });
  }

  return() {
    this.router.navigate(['/dashboard']);
  }
}
