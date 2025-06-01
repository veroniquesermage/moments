import {Component, Input} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
@Component({
  selector: 'app-gift-header',
  standalone: true,
  imports: [
    CommonModule
  ],
  templateUrl: './gift-header.component.html',
  styleUrl: './gift-header.component.scss'
})
export class GiftHeaderComponent {

  @Input()
  gift!: GiftPublicResponse;

}
