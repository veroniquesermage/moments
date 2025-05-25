import {Component, EventEmitter, Input, Output} from '@angular/core';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {CommonModule} from '@angular/common';

@Component({
  selector: 'app-gift-delivery',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './gift-delivery.component.html',
  styleUrl: './gift-delivery.component.scss'
})
export class GiftDeliveryComponent {
  @Input()
  giftDetailResponse!: GiftDetailResponse;

  @Output() receptionToggled = new EventEmitter<boolean>();

  toggleRecu() {
    this.receptionToggled.emit(!this.giftDetailResponse.gift.recu);
  }

}
