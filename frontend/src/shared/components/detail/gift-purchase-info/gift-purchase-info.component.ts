import {Component, Input} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftPurchaseInfoSchema} from 'src/core/models/gift/gift-purchase-info.model';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';
import {FormatMontantPipe} from 'src/core/pipes/format-montant.pipe';

@Component({
  selector: 'app-gift-purchase-info',
  standalone: true,
  imports: [
    CommonModule,
    DisplayNamePipe,
    FormatMontantPipe
  ],
  templateUrl: './gift-purchase-info.component.html',
  styleUrl: './gift-purchase-info.component.scss'
})
export class GiftPurchaseInfoComponent {
  @Input()
  purchaseInfo!: GiftPurchaseInfoSchema;

}
