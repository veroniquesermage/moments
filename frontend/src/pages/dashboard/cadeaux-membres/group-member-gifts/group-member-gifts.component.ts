import {Component, OnInit} from '@angular/core';
import {GiftTableComponent} from 'src/shared/components/gift-table/gift-table.component';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {UserGroupService} from 'src/core/services/userGroup.service';
import {User} from 'src/security/model/user.model';
import {NgForOf, NgIf} from '@angular/common';
import {GroupStateService} from 'src/core/services/groupState.service';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {Gift} from 'src/core/models/gift/gift.model';

@Component({
  selector: 'app-group-member-gifts',
  standalone: true,
  imports: [
    GiftTableComponent,
    NgForOf,
    NgIf,
    TerminalModalComponent
  ],
  templateUrl: './group-member-gifts.component.html',
  styleUrl: './group-member-gifts.component.scss'
})
export class GroupMemberGiftsComponent implements OnInit {

  users: User[] | undefined = [];
  selectedMember: User | undefined = undefined;

  displayedColumns = [
    {key: 'nom', label: 'Nom'},
    {key: 'prix', label: 'Prix (€)', formatFn: (v: number) => `${v} €`},
    {key: 'priorite', label: 'Priorité'},
    {key: 'statut', label: 'Statut'}
  ];

  constructor(public giftService: GiftService,
              public userGroupService: UserGroupService,
              public router: Router,
              private groupStateService: GroupStateService,
              public errorService: ErrorService) {
  }

  async ngOnInit() {
    console.log('📦 Groupe courant :', this.groupStateService.getSelectedGroup());
    this.giftService.clearGifts();

    const idGroup = this.groupStateService.getSelectedGroup()?.id;
    const result = await this.userGroupService.fetchUserGroup(idGroup!);
    if (result.success) {
      this.users = result.data;

      const savedId = this.userGroupService.getSelectedMemberId();
      if (savedId) {
        const found = this.users?.find(u => u.id === savedId);
        if (found) {
          this.selectMember(found);
        }
      }
    } else {
      this.errorService.showError(result.message);
    }
  }

  onGiftClicked(gift: Gift): void {
    this.router.navigate(['/dashboard/cadeau', gift.id], {
      queryParams: { context: 'cadeaux-groupe' }
    });
  }

  retour() {
    this.selectedMember = undefined;
    this.userGroupService.setSelectedMemberId(null);
    this.giftService.clearGifts();
    this.router.navigate(['/dashboard']);
  }

  async selectMember(user: User | undefined) {
    this.selectedMember = user;
    this.userGroupService.setSelectedMemberId(user ? user.id : null);

    const result = await this.giftService.fetchGifts(user?.id);

    if(!result.success){
      this.errorService.showError("❌ Impossible d\'afficher la liste de ce membre. Veuillez réessayer plus tard.");
    }
  }
}
