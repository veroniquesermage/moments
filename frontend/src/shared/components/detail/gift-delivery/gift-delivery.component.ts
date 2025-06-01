import {Component, EventEmitter, Input, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftDelivery} from 'src/core/models/gift/gift-delivery.model';

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
  giftDelivery!: GiftDelivery;

  @Output() receptionToggled = new EventEmitter<boolean>();

  toggleRecu() {
    this.receptionToggled.emit(!this.giftDelivery.recu);
  }

}
