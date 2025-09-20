import {Component, inject, OnInit, signal} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {SharingService} from 'src/core/services/sharing.service';
import {GiftShared} from 'src/core/models/gift/gift-shared.model';
import {FormsModule} from '@angular/forms';
import {GiftSharedDraft} from 'src/core/models/gift/gift-shared-draft.model';
import {CommonModule} from '@angular/common';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GroupContextService} from 'src/core/services/group-context.service';
import {UserDisplay} from 'src/core/models/user-display.model';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';
import {UserService} from 'src/core/services/user.service';
@Component({
  selector: 'app-gift-sharing',
  standalone: true,
  imports: [
    FormsModule,
    CommonModule,
    DisplayNamePipe,
  ],
  templateUrl: './gift-sharing.component.html',
  styleUrl: './gift-sharing.component.scss'
})
export class GiftSharingComponent implements OnInit {

  private route = inject(ActivatedRoute);
  idGift?: number | undefined = undefined;
  partages: GiftShared[] | undefined = [];
  partagesDraft: GiftSharedDraft[] = [];
  gift: GiftPublicResponse | undefined = undefined;
  members = signal<UserDisplay[]>([]);
  isLoadingMembers = signal<boolean>(false);
  contextBrut: string | null = null;

  constructor(private sharingService: SharingService,
              private giftService: GiftService,
              private groupContextService: GroupContextService,
              public router: Router,
              public errorService: ErrorService,
              private userService: UserService) {
  }

  async ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.idGift = idParam ? +idParam : undefined;
    this.contextBrut = this.route.snapshot.queryParamMap.get('context');

    if(!this.idGift){
      this.errorService.showError("❌ Impossible de modifier le partage.");
      return;
    }

    await this.loadMembers();

    const result = await this.giftService.getGift(this.idGift);
    if (result.success) {
      this.gift = result.data.gift;
      this.partages = result.data.partage;
    } else {
      this.errorService.showError("❌ Impossible de modifier le partage.");
    }
  }

  private async loadMembers(): Promise<void> {
    const groupId = this.groupContextService.getGroupId();
    if (!groupId) {
      this.errorService.showError('❌ Aucun groupe actif.');
      return;
    }

    this.isLoadingMembers.set(true);
    try {
      const result = await this.userService.fetchUserGroup(groupId);
      if (result.success) {
        this.members.set(result.data);
      } else {
        this.errorService.showError(result.message);
      }
    } finally {
      this.isLoadingMembers.set(false);
    }
  }

  async supprimerLigne(index: number) {
    const sharedId = this.partages![index].id;
    const result = await this.sharingService.deleteShare(sharedId);

    if (result.success) {
      this.partages!.splice(index, 1);
    } else {
      this.errorService.showError(result.message);
    }


  }

  ajouterLigne() {
    console.log("Ajout d'une ligne");
    this.partagesDraft.push({
      participant: null,
      montant: null
    });
    console.log("partagesDraft actuels :", this.partagesDraft);
  }

  supprimerDraft(index: number) {
    this.partagesDraft.splice(index, 1);
  }

  retourEnArriere(){
    void this.router.navigate(['/dashboard/cadeau', this.idGift], {
      queryParams: { context: this.contextBrut }
    });
  }

  async enregistrerPartages() {
    const draftsValides = this.partagesDraft.filter(
      draft => draft.participant && draft.montant != null
    );

    const draftConvertis: GiftShared[] = draftsValides.map(draft => ({
      id: 0, // ou undefined, à ignorer côté backend si auto-généré
      preneur: this.gift!.reservePar!,
      cadeauId: this.gift!.id,
      participant: draft.participant!,
      montant: draft.montant!,
      rembourse: false
    }));

    const allPartages: GiftShared[] = [
      ...(this.partages ?? []),
      ...draftConvertis
    ];
    console.log('💾 Partages complets à envoyer :', allPartages);

    const result = await this.sharingService.saveAllShares(allPartages, this.idGift! );
    if(result.success){
      console.log('retour au cadeau avec context : ', this.contextBrut);
      await this.router.navigate(['/dashboard/cadeau', this.idGift], {
        queryParams: { context: this.contextBrut }
      });
    } else {
      this.errorService.showError("❌ Une erreur est survenue à l'enregistrement.")
    }
  }

}
