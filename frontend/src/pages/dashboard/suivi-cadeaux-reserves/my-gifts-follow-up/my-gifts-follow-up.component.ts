import {Component, computed, OnDestroy, OnInit} from '@angular/core';
import {formatDate, NgForOf, NgIf, TitleCasePipe} from '@angular/common';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {User} from 'src/security/model/user.model';
import {Subscription} from 'rxjs';
import {ViewportService} from 'src/core/services/viewport.service';
import {ColumnDefinition} from 'src/core/models/column-definition.model';
import {GiftFollowed} from 'src/core/models/gift/gift-followed.model';
import {GiftTableColumn} from 'src/core/models/gift/gift-table-column.model';
import {UserDisplay} from 'src/core/models/user-display.model';
import {getDisplayName} from 'src/core/utils/display-name';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {GiftFollowedByAccount} from 'src/core/models/gift/gift-followed-by-account.model';
import {AuthService} from 'src/security/service/auth.service';
import {FormatMontantPipe} from 'src/core/pipes/format-montant.pipe';
import {formatEuro} from 'src/core/utils/format-montant';

@Component({
  selector: 'app-my-gifts-follow-up',
  standalone: true,
  imports: [
    NgIf,
    TerminalModalComponent,
    NgForOf,
    TitleCasePipe,
    FeedbackTestComponent,
    FormatMontantPipe,
  ],
  templateUrl: './my-gifts-follow-up.component.html',
  styleUrl: './my-gifts-follow-up.component.scss'
})
export class MyGiftsFollowUpComponent implements OnInit, OnDestroy{

  giftsFollowedByAccount: GiftFollowedByAccount[] = []
  displayedColumns: ColumnDefinition[] = [];
  portraitSub?: Subscription;
  isPortrait = false;
  profile = computed(() => this.authService.profile())

  readonly displayedColumnsPortrait:  ColumnDefinition[] = [
    {key: 'destinataire', label: 'Destinataire', formatFn: (u: UserDisplay | null | undefined) => getDisplayName(u)},
    { key: 'nom', label: 'Nom' },
    {key: 'prixReel', label: 'Prix payé (€)', formatFn: formatEuro},
    { key: 'statut', label: 'Statut' }
  ];

  readonly displayedColumnsDesktop:  ColumnDefinition[] = [
    {key: 'destinataire', label: 'Destinataire', formatFn: (u: User | null | undefined) => getDisplayName(u)},
    {key: 'nom', label: 'Nom'},
    {key: 'magasin', label: 'Magasin'},
    {key: 'quantite', label: 'Qté'},
    {key: 'prixReel', label: 'Prix payé (€)', formatFn: formatEuro},
    {key: 'lieuLivraison', label: 'Lieu de livraison'},
    {key: 'dateLivraison', label: 'Date de livraison', formatFn: (v: string) => v ? formatDate(v, 'dd-MM', 'fr-FR') : '—'},
    {key: 'statut', label: 'Statut'}
  ];

  constructor( public giftService: GiftService,
               private authService: AuthService,
               private viewport: ViewportService,
               private router : Router,
               public  errorService: ErrorService) {
  }

  async ngOnInit() {
    this.giftService.clearGifts();
    this.portraitSub = this.viewport.isPortrait$.subscribe(isPortrait => {
      this.isPortrait = isPortrait; // <-- tu le stockes ici
      this.displayedColumns = isPortrait
        ? this.displayedColumnsPortrait
        : this.displayedColumnsDesktop;
    });
    const result = await this.giftService.getFollowedGifts();

    if(result.success){
      this.giftsFollowedByAccount = result.data;
    } else {
      this.errorService.showError(result.message);
    }
  }

  ngOnDestroy(): void {
    this.portraitSub?.unsubscribe();
  }

  onGiftClicked(gift: GiftFollowed): void {
    void this.router.navigate(['/dashboard/cadeau', gift.gift.id], {
      queryParams: { context: 'suivi' }
    });
  }

  async retour() {
      await this.router.navigate(['/dashboard']);
  }

  getAriaLabel(giftFollowed: GiftFollowed): string | null {
    if (giftFollowed.gift.statut === 'PARTAGE') return 'Cadeau partagé';
    if (giftFollowed.gift.statut === 'PRIS') return 'Cadeau pris';
    return null; // ne vocalise rien si aucune condition n’est remplie
  }

  getGiftValue(giftFollowed: GiftFollowed, column: GiftTableColumn): any {
    let rawValue: any;

    // Gestion manuelle des colonnes composites
    switch (column.key) {
      case 'nom':
      case 'statut':
      case 'quantite':
      case 'magasin':
        rawValue = giftFollowed.gift[column.key];
        break;
      case 'destinataire':
        rawValue = giftFollowed.gift.destinataire;
        break;
      case 'prixReel':
        if (giftFollowed.partage?.participant?.id === this.profile()?.id) {
          rawValue = giftFollowed.partage?.montant;
        } else {
          rawValue = giftFollowed.purchaseInfo?.prixReel;
        }
        break;

      case 'lieuLivraison':
        rawValue = giftFollowed.delivery?.lieuLivraison;
        break;
      case 'dateLivraison':
        rawValue = giftFollowed.delivery?.dateLivraison;
        break;
      default:
        rawValue = undefined;
    }

    return column.formatFn ? column.formatFn(rawValue, giftFollowed) : rawValue;
  }


  protected readonly Number = Number;
  composant: string = "MyGiftsFollowUpComponent";
}
