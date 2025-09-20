import {Component, OnInit, signal} from '@angular/core';
import {GiftService} from 'src/core/services/gift.service';
import {Router, ActivatedRoute} from '@angular/router';
import {CommonModule} from '@angular/common';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftTableColumn} from 'src/core/models/gift/gift-table-column.model';
import {GroupContextService} from 'src/core/services/group-context.service';
import {UserDisplay} from 'src/core/models/user-display.model';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';
import {formatEuro} from 'src/core/utils/format-montant';
import {PaginationComponent} from 'src/shared/components/pagination/pagination.component';
import {PaginationInfo} from 'src/core/models/common/pagination.model';
import {UserService} from 'src/core/services/user.service';

@Component({
  selector: 'app-group-member-gifts',
  standalone: true,
  imports: [
    CommonModule,
    TerminalModalComponent,
    DisplayNamePipe,
    PaginationComponent
  ],
  templateUrl: './group-member-gifts.component.html',
  styleUrl: './group-member-gifts.component.scss'
})
export class GroupMemberGiftsComponent implements OnInit {

  protected readonly DisplayNamePipe = DisplayNamePipe;
  members = signal<UserDisplay[]>([]);
  selectedMember: UserDisplay | undefined = undefined;
  giftPublic: GiftPublicResponse[] = [];
  currentPage = signal(1);
  paginationInfo = signal<PaginationInfo | null>(null);
  isLoadingMember = signal<boolean>(false);
  isLoadingMembers = signal<boolean>(false);

  displayedColumns = [
    {key: 'nom', label: 'Titre du cadeau'},
    {key: 'prix', label: 'Prix unitaire (€)', formatFn: formatEuro},
    {key: 'fraisPort', label: 'Frais de port (€)', formatFn: formatEuro},
    {key: 'quantite', label: 'Quantité'},
    {key: 'statut', label: 'Statut'}
  ];

  constructor(public giftService: GiftService,
              public router: Router,
              private route: ActivatedRoute,
              private groupContextService: GroupContextService,
              private userService: UserService,
              public errorService: ErrorService) {
  }

  async ngOnInit() {
    this.giftService.clearGifts();

    // 1. Charger les membres du groupe
    await this.loadMembers();

    // 2. Vérifier les query params pour restaurer l'état
    const memberId = this.route.snapshot.queryParams['memberId'];
    const page = this.route.snapshot.queryParams['page'];

    if (memberId && page) {
      const members = this.members();
      const member = members.find(m => m.id?.toString() === memberId);
      if (member) {
        this.selectedMember = member;
        await this.loadMemberGifts(member.id!, parseInt(page, 10));
      }
    }
  }

  private async loadMembers(): Promise<void> {
    const groupId = this.groupContextService.getGroupId();
    if (!groupId) {
      console.error('[GroupMemberGifts] Aucun groupId trouvé');
      return;
    }

    this.isLoadingMembers.set(true);
    console.log('[GroupMemberGifts] Chargement des membres pour le groupe', groupId);

    try {
      const result = await this.userService.fetchUserGroup(groupId);
      if (result.success) {
        this.members.set(result.data);
        console.log('[GroupMemberGifts] Membres chargés:', result.data.length);
      } else {
        console.error('[GroupMemberGifts] Erreur lors du chargement des membres:', result.message);
        this.errorService.showError("❌ Impossible de charger les membres du groupe");
      }
    } catch (error) {
      console.error('[GroupMemberGifts] Exception lors du chargement des membres:', error);
      this.errorService.showError("❌ Erreur lors du chargement des membres");
    } finally {
      this.isLoadingMembers.set(false);
    }
  }

  onGiftClicked(gift: GiftPublicResponse): void {
    const queryParams: any = { context: 'cadeaux-groupe' };

    // Ajouter memberId et page si un membre est sélectionné
    if (this.selectedMember?.id) {
      queryParams.memberId = this.selectedMember.id;
      queryParams.page = this.currentPage();
    }

    void this.router.navigate(['/dashboard/cadeau', gift.id], {
      queryParams
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
