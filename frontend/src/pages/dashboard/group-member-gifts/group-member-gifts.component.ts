import {Component, OnInit} from '@angular/core';
import {GiftTableComponent} from 'src/shared/components/gift-table/gift-table.component';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';
import {Gift} from 'src/core/models/gift.model';
import {UserGroupService} from 'src/core/services/userGroup.service';
import {User} from 'src/security/model/user.model';
import {NgForOf} from '@angular/common';
import {GroupStateService} from 'src/core/services/groupState.service';

@Component({
  selector: 'app-group-member-gifts',
  standalone: true,
  imports: [
    GiftTableComponent,
    NgForOf
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
              private groupStateService: GroupStateService) {
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
    }
  }

  onGiftClicked(gift: Gift): void {
    this.router.navigate(['/dashboard/leurs-cadeaux', gift.id]);
  }

  retour() {
    this.selectedMember = undefined;
    this.userGroupService.setSelectedMemberId(null);
    this.giftService.clearGifts();
    this.router.navigate(['/dashboard']);
  }

  selectMember(user: User | undefined) {
    this.selectedMember = user;
    this.userGroupService.setSelectedMemberId(user ? user.id : null);
    this.giftService.fetchGifts(user?.id);
  }
}
