import {Component, inject, OnInit} from '@angular/core';
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
import {
  RefreshGroupMembersComponent
} from 'src/shared/components/refresh-group-members/refresh-group-members.component';
import {UserDisplay} from 'src/core/models/user-display.model';
import {DisplayNamePipe} from 'src/core/pipes/display-name.pipe';

@Component({
  selector: 'app-gift-sharing',
  standalone: true,
  imports: [
    FormsModule,
    CommonModule,
    RefreshGroupMembersComponent,
    DisplayNamePipe
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
  membresDisponibles: UserDisplay[] = [];
  contextBrut: string | null = null;

  constructor(private sharingService: SharingService,
              private giftService: GiftService,
              private groupContextService: GroupContextService,
              public router: Router,
              public errorService: ErrorService) {
  }

  async ngOnInit() {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.idGift = idParam ? +idParam : undefined;
    this.contextBrut = this.route.snapshot.queryParamMap.get('context');

    if(!this.idGift){
      this.errorService.showError("❌ Impossible de modifier le partage.");
      return;
    }
    const result = await this.giftService.getGift(this.idGift);
    if (result.success) {
      this.gift = result.data.gift;
      this.partages = result.data.partage;
    } else {
      this.errorService.showError("❌ Impossible de modifier le partage.");
    }

    this.membresDisponibles = await this.groupContextService.getGroupMembers();
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
    console.log("partagesDraft actuels :", this.partagesDraft);
  }

  supprimerDraft(index: number) {
    this.partagesDraft.splice(index, 1);
  }

  retourEnArriere(){
    this.router.navigate(['/dashboard/cadeau', this.idGift], {
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
