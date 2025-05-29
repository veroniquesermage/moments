import {Component, inject, OnInit} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {SharingService} from 'src/core/services/sharing.service';
import {Gift} from 'src/core/models/gift/gift.model';
import {GiftShared} from 'src/core/models/gift/gift_shared.model';
import {FormsModule} from '@angular/forms';
import {GiftSharedDraft} from 'src/core/models/gift/gift-shared-draft.model';
import {CommonModule} from '@angular/common';
import {User} from 'src/security/model/user.model';
import {UserGroupService} from 'src/core/services/user-group.service';
import {GroupStateService} from 'src/core/services/group-state.service';

@Component({
  selector: 'app-gift-sharing',
  standalone: true,
  imports: [
    FormsModule,
    CommonModule
  ],
  templateUrl: './gift-sharing.component.html',
  styleUrl: './gift-sharing.component.scss'
})
export class GiftSharingComponent implements OnInit {

  private route = inject(ActivatedRoute);
  id?: number | undefined = undefined;
  partages: GiftShared[] | undefined = [];
  partagesDraft: GiftSharedDraft[] = [];
  gift: Gift | undefined = undefined;
  membresDisponibles: User[] = [];
  contextBrut: string | null = null;

  constructor(private sharingService: SharingService,
              private giftService: GiftService,
              private userGroupService: UserGroupService,
              private groupStateService: GroupStateService,
              public router: Router,
              public errorService: ErrorService) {
  }

  async ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.id = idParam ? +idParam : undefined;
    this.contextBrut = this.route.snapshot.queryParamMap.get('context');

    if(!this.id){
      this.errorService.showError("❌ Impossible de modifier le partage.");
      return;
    }
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.gift = result.data.gift;         // 🧠 le cadeau lui-même
      this.partages = result.data.partage;
    } else {
      this.errorService.showError("❌ Impossible de modifier le partage.");
    }
    const groupUsers = await this.userGroupService.fetchUserGroup(this.groupStateService.getSelectedGroup()!.id);

    if(groupUsers.success){
      this.membresDisponibles = groupUsers.data;
    } else {
      this.membresDisponibles = [];
    }
  }

  supprimerLigne(index: number) {
    this.partages!.splice(index, 1);
  }

  ajouterLigne() {
    console.log("Ajout d'une ligne");
    this.partagesDraft.push({
      participant: null,
      montant: null
    });
    console.log("partagesDraft ACTUEL :", this.partagesDraft);
  }

  supprimerDraft(index: number) {
    this.partagesDraft.splice(index, 1);
  }

  retourEnArriere(){
    this.router.navigate(['/dashboard/cadeau', this.id], {
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

    const result = await this.sharingService.saveAllShares(allPartages, this.id! );
    if(result.success){
      console.log('retour au cadeau avec context : ', this.contextBrut);
      await this.router.navigate(['/dashboard/cadeau', this.id], {
        queryParams: { context: this.contextBrut }
      });
    } else {
      this.errorService.showError("❌ Une erreur est survenue à l'enregistrement.")
    }
  }

}
