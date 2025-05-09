import {Component, inject} from '@angular/core';
import {GiftTableComponent} from 'src/shared/components/gift-table/gift-table.component';
import {GiftDetailComponent} from 'src/shared/components/gift-detail/gift-detail.component';
import {ActivatedRoute} from '@angular/router';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-gift-detail-page',
  standalone: true,
  imports: [
    CommonModule,
    GiftDetailComponent
  ],
  templateUrl: './gift-detail-page.component.html',
  styleUrl: './gift-detail-page.component.scss'
})
export class GiftDetailPageComponent {

  private route = inject(ActivatedRoute);
  giftId: number | undefined = undefined;
  context: "own" | "other";

  constructor() {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.context = this.route.snapshot.data['context'] as 'own' | 'other';

    this.giftId = idParam ? +idParam : undefined;
  }
}
