import {Component, Input} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {FormatMontantPipe} from 'src/core/pipes/format-montant.pipe';

@Component({
  selector: 'app-gift-header',
  standalone: true,
  imports: [
    CommonModule,
    FormatMontantPipe
  ],
  templateUrl: './gift-header.component.html',
  styleUrl: './gift-header.component.scss'
})
export class GiftHeaderComponent {

  @Input()
  gift!: GiftPublicResponse;

}
