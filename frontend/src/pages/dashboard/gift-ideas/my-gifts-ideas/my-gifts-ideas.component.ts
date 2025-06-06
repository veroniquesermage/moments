import {Component, OnInit} from '@angular/core';
import {NgForOf, NgIf} from '@angular/common';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GiftIdeasResponse} from 'src/core/models/gift/gift-ideas-response.model';
import {IdeaService} from 'src/core/services/idea.service';
import {ErrorService} from 'src/core/services/error.service';
import {Router} from '@angular/router';

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
              private router: Router,
              public errorService: ErrorService) {
  }

  async ngOnInit() {

    const result = await this.ideaService.fetchIdeas();

    if(result.success){
      this.giftIdeas = result.data
    } else {
      this.errorService.showError(result.message);
    }
  }

  onRowClick(gift: GiftIdeasResponse){

  }

  toggleVisibilite(ideaId: number){

  }

  return(){
    this.router.navigate(['/dashboard']);
  }

  goToAjout(){
    this.router.navigate(['/dashboard/idees/creer']);
  }

}
