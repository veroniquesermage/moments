import {Component, OnInit} from '@angular/core';
import {NgForOf, NgIf} from '@angular/common';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GiftIdeasResponse} from 'src/core/models/gift/gift-ideas-response.model';
import {IdeaService} from 'src/core/services/idea.service';
import {ErrorService} from 'src/core/services/error.service';
import {Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {GiftStatus} from 'src/core/enum/gift-status.enum';
import {GiftStatutDTO} from 'src/core/models/gift/gift-statut.model';

@Component({
  selector: 'app-my-gifts-ideas',
  standalone: true,
  imports: [
    NgForOf,
    NgIf,
    TerminalModalComponent
  ],
  templateUrl: './my-gifts-ideas.component.html',
  styleUrl: './my-gifts-ideas.component.scss'
})
export class MyGiftsIdeasComponent implements OnInit{

  giftIdeas: GiftIdeasResponse[] = [];

  constructor(private ideaService: IdeaService,
              private giftService: GiftService,
              private router: Router,
              public errorService: ErrorService) {
  }

  async ngOnInit() {
    await this.loadIdeas();
  }

  onRowClick(gift: GiftIdeasResponse){
    this.router.navigate(['/dashboard/cadeau', gift.gift.id], {
      queryParams: { context: 'idee-cadeau' }
    });
  }

  return(){
    this.router.navigate(['/dashboard']);
  }

  goToAjout(){
    this.router.navigate(['/dashboard/idees/creer']);
  }

  duplicateIdea() {

  }

  async takeIt(id: number) {
    const giftStatut : GiftStatutDTO = {
      status: GiftStatus.PRIS
    }
    const result = await this.giftService.changeStatusGift(id, giftStatut);

    if(result.success){
      await this.loadIdeas();
    } else{
      this.errorService.showError("❌ Erreur lors de la tentative de prendre le cadeau, veuillez réessayer plus tard.")
    }
  }

  changeVisibility() {

  }

  async loadIdeas() {
    const result = await this.ideaService.fetchIdeas();
    if(result.success){
      this.giftIdeas = result.data
    } else {
      this.errorService.showError(result.message);
    }
  }
}
