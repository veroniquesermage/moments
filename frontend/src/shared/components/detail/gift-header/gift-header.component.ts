import {Component, Input} from '@angular/core';
import {Gift} from 'src/core/models/gift/gift.model';
import {CommonModule} from '@angular/common';
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
  gift!: Gift;

}
