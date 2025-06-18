import {Component, Input} from '@angular/core';
import {CommonModule} from '@angular/common';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';

@Component({
  selector: 'app-gift-idea',
  standalone: true,
  imports: [
    CommonModule,
    DisplayNamePipe
  ],
  templateUrl: './gift-idea.component.html',
  styleUrl: './gift-idea.component.scss'
})
export class GiftIdeaComponent {

  @Input()
  giftDetail!: GiftDetailResponse;
  @Input()
  currentUserId!: number;

  isMyIdea(): boolean{
    return this.giftDetail.ideas?.proposeePar.id == this.currentUserId
  }

}
