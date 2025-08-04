import {Component, OnInit, Signal} from '@angular/core';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftTableColumn} from 'src/core/models/gift/gift-table-column.model';
import {GroupContextService} from 'src/core/services/group-context.service';
import {UserDisplay} from 'src/core/models/user-display.model';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {formatEuro} from 'src/core/utils/format-montant';

@Component({
  selector: 'app-group-member-gifts',
  standalone: true,
  imports: [
    CommonModule,
    TerminalModalComponent,
    DisplayNamePipe,
    FeedbackTestComponent
  ],
  templateUrl: './group-member-gifts.component.html',
  styleUrl: './group-member-gifts.component.scss'
})
export class GroupMemberGiftsComponent implements OnInit {

  protected readonly DisplayNamePipe = DisplayNamePipe;
  composant: string = "GroupMemberGiftsComponent";
  membersSignal: Signal<UserDisplay[]>;
  selectedMember: UserDisplay | undefined = undefined;
  giftPublic: GiftPublicResponse[] = []

  displayedColumns = [
    {key: 'nom', label: 'Nom'},
    {key: 'prix', label: 'Prix unitaire (€)', formatFn: formatEuro},
    {key: 'fraisPort', label: 'Frais de port (€)', formatFn: formatEuro},
    {key: 'quantite', label: 'Quantité'},
    {key: 'statut', label: 'Statut'}
  ];

  constructor(public giftService: GiftService,
              public router: Router,
              private groupContextService: GroupContextService,
              public errorService: ErrorService) {
    this.membersSignal = this.groupContextService.getMembersSignal();
  }

  async ngOnInit() {
    this.giftService.clearGifts();
  }

  onGiftClicked(gift: GiftPublicResponse): void {
    void this.router.navigate(['/dashboard/cadeau', gift.id], {
      queryParams: { context: 'cadeaux-groupe' }
    });
  }

  retour() {
    this.selectedMember = undefined;
    this.giftService.clearGifts();
    void this.router.navigate(['/dashboard']);
  }

  async selectMember(user: UserDisplay) {
    this.selectedMember = user;

    if(!user.id){
      this.errorService.showError("❌ Impossible d\'accéder au membre. Veuillez réessayer plus tard.");
    }
    const result = await this.giftService.getVisibleGiftsForMember(user!.id);
    if (result.success) {
      this.giftPublic = [ ...result.data.filter(gift => gift.priorite !==0),
                          ...result.data.filter(gift => gift.priorite === 0)];
    }else {
      this.errorService.showError("❌ Impossible d\'afficher la liste de ce membre. Veuillez réessayer plus tard.");
    }
  }

  getAriaLabel(giftPublic: GiftPublicResponse): string | null {
    if (giftPublic.statut === 'PRIS') return 'Cadeau pris';
    return null; // ne vocalise rien si aucune condition n’est remplie
  }

  getGiftValue(gift: GiftPublicResponse, column: GiftTableColumn): any {
    const rawValue = (gift as any)[column.key];
    return column.formatFn ? column.formatFn(rawValue, gift) : rawValue;
  }

}
