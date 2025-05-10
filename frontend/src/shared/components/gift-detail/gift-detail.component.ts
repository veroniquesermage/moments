import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Gift} from 'src/core/models/gift.model';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {
  TerminalConfirmModalComponent
} from 'src/shared/components/terminal-confirm-modal/terminal-confirm-modal.component';

@Component({
  selector: 'app-gift-detail',
  standalone: true,
  imports: [CommonModule, TerminalConfirmModalComponent],
  templateUrl: './gift-detail.component.html',
  styleUrl: './gift-detail.component.scss'
})
export class GiftDetailComponent implements OnInit{

  @Input() id!: number;
  @Input() context: 'own' | 'other' = 'own';
  @Output() back = new EventEmitter<void>();
  gift: Gift | undefined = undefined;
  showDeleteConfirm = false;


  constructor(public giftService: GiftService,
              public router : Router) {
  }

  async ngOnInit(): Promise<void> {
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.gift = result.data;
    }
  }

  modifier() {
    this.router.navigate(['/dashboard/mes-cadeaux/modifier', this.gift?.id]);
  }

  requestDelete() {
    this.showDeleteConfirm = true;
  }

  cancelDelete() {
    this.showDeleteConfirm = false;
  }

  async confirmDelete() {
    if (!this.gift) return;
    await this.giftService.deleteGift(this.gift.id!);
    await this.router.navigate(['/dashboard/mes-cadeaux']);
  }


}
