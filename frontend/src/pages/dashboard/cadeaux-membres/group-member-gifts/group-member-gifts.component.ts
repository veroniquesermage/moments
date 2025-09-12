import {Component, OnInit, Signal, signal} from '@angular/core';
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
import {PaginationComponent} from 'src/shared/components/pagination/pagination.component';
import {PaginationInfo} from 'src/core/models/common/pagination.model';

@Component({
  selector: 'app-group-member-gifts',
  standalone: true,
  imports: [
    CommonModule,
    TerminalModalComponent,
    DisplayNamePipe,
    FeedbackTestComponent,
    PaginationComponent
  ],
  templateUrl: './group-member-gifts.component.html',
  styleUrl: './group-member-gifts.component.scss'
})
export class GroupMemberGiftsComponent implements OnInit {

  protected readonly DisplayNamePipe = DisplayNamePipe;
  composant: string = "GroupMemberGiftsComponent";
  membersSignal: Signal<UserDisplay[]>;
  selectedMember: UserDisplay | undefined = undefined;
  giftPublic: GiftPublicResponse[] = [];
  currentPage = signal(1);
  paginationInfo = signal<PaginationInfo | null>(null);
  isLoadingMember = signal<boolean>(false);

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

  async selectMember(user: UserDisplay): Promise<void> {
    this.selectedMember = user;

    if(!user.id){
      this.errorService.showError("❌ Impossible d\'accéder au membre. Veuillez réessayer plus tard.");
      return;
    }
    
    await this.loadMemberGifts(user.id, 1);
  }

  async loadMemberGifts(userId: number, page: number): Promise<void> {
    this.isLoadingMember.set(true);
    
    const result = await this.giftService.getVisibleGiftsForMember(userId, page);
    if (result.success && result.data) {
      this.currentPage.set(page);
      this.paginationInfo.set(result.data.pagination);
      // Tri par priorité : priorités non nulles d\'abord, puis nulles
      this.giftPublic = [ ...result.data.items.filter(gift => gift.priorite !==0),
                          ...result.data.items.filter(gift => gift.priorite === 0)];
    } else {
      this.errorService.showError("❌ Impossible d\'afficher la liste de ce membre. Veuillez réessayer plus tard.");
    }
    
    this.isLoadingMember.set(false);
  }

  async onPageChange(page: number): Promise<void> {
    if (this.selectedMember?.id) {
      await this.loadMemberGifts(this.selectedMember.id, page);
      window.scrollTo({ top: 0, behavior: 'smooth' });
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
