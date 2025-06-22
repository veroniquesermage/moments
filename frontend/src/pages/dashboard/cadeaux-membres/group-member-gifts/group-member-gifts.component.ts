import {Component, OnInit} from '@angular/core';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {UserGroupService} from 'src/core/services/user-group.service';
import {CommonModule} from '@angular/common';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftTableColumn} from 'src/core/models/gift/gift-table-column.model';
import {GroupContextService} from 'src/core/services/group-context.service';
import {
  RefreshGroupMembersComponent
} from 'src/shared/components/refresh-group-members/refresh-group-members.component';
import {UserDisplay} from 'src/core/models/user-display.model';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';

@Component({
  selector: 'app-group-member-gifts',
  standalone: true,
  imports: [
    CommonModule,
    TerminalModalComponent,
    RefreshGroupMembersComponent,
    DisplayNamePipe,
    FeedbackTestComponent
  ],
  templateUrl: './group-member-gifts.component.html',
  styleUrl: './group-member-gifts.component.scss'
})
export class GroupMemberGiftsComponent implements OnInit {

  protected readonly DisplayNamePipe = DisplayNamePipe;
  composant: string = "GroupMemberGiftsComponent";
  users: UserDisplay[] | undefined = [];
  selectedMember: UserDisplay | undefined = undefined;
  giftPublic: GiftPublicResponse[] = []

  displayedColumns = [
    {key: 'nom', label: 'Nom'},
    {key: 'prix', label: 'Prix (€)', formatFn: (v: number | null | undefined) => v != null ? `${v} €` : '-'},
    {key: 'fraisPort', label: 'Frais de port (€)', formatFn: (v: number | null | undefined) => v != null ? `${v} €` : '-'},
    {key: 'quantite', label: 'Quantité'},
    {key: 'statut', label: 'Statut'}
  ];

  constructor(public giftService: GiftService,
              public userGroupService: UserGroupService,
              public router: Router,
              private groupContextService: GroupContextService,
              public errorService: ErrorService) {
  }

  async ngOnInit() {
    this.giftService.clearGifts();
    try {
      this.users = await this.groupContextService.getGroupMembers();
    }  catch (err) {
      this.errorService.showError("❌ Impossible de récupérer les membres du groupe. Veuillez réessayer plus tard.");
    }
  }

  onGiftClicked(gift: GiftPublicResponse): void {
    this.router.navigate(['/dashboard/cadeau', gift.id], {
      queryParams: { context: 'cadeaux-groupe' }
    });
  }

  retour() {
    this.selectedMember = undefined;
    this.giftService.clearGifts();
    this.router.navigate(['/dashboard']);
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
