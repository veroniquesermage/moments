import {Component, OnDestroy, OnInit} from '@angular/core';
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

@Component({
  selector: 'app-my-gifts-follow-up',
  standalone: true,
  imports: [
    NgIf,
    TerminalModalComponent,
    NgForOf,
    TitleCasePipe,
  ],
  templateUrl: './my-gifts-follow-up.component.html',
  styleUrl: './my-gifts-follow-up.component.scss'
})
export class MyGiftsFollowUpComponent implements OnInit, OnDestroy{

  giftsFollowed: GiftFollowed[] = []
  displayedColumns: ColumnDefinition[] = [];
  portraitSub?: Subscription;
  isPortrait = false;


  readonly displayedColumnsPortrait:  ColumnDefinition[] = [
    {key: 'destinataire', label: 'Destinataire', formatFn: (u: User | null | undefined) => u?.prenom || '—' },
    { key: 'nom', label: 'Nom' },
    {key: 'prixReel', label: 'Prix réel (€)', formatFn: (v: number | null) => v != null ? `${v}€` : '—'},
    { key: 'statut', label: 'Statut' }
  ];

  readonly displayedColumnsDesktop:  ColumnDefinition[] = [
    {key: 'destinataire', label: 'Destinataire', formatFn: (u: User | null | undefined) => u?.prenom || '—' },
    {key: 'nom', label: 'Nom'},
    {key: 'magasin', label: 'Magasin'},
    {key: 'quantite', label: 'Quantité'},
    {key: 'prixReel', label: 'Prix réel (€)', formatFn: (v: number | null) => v != null ? `${v}€` : '—'},
    {key: 'lieuLivraison', label: 'Lieu de livraison'},
    {key: 'dateLivraison', label: 'Date de livraison', formatFn: (v: string) => v ? formatDate(v, 'dd-MM-yyyy', 'fr-FR') : '—'},
    {key: 'statut', label: 'Statut'}
  ];

  constructor( public giftService: GiftService,
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
      this.giftsFollowed = result.data;
    } else {
      this.errorService.showError(result.message);
    }
  }

  ngOnDestroy(): void {
    this.portraitSub?.unsubscribe();
  }

  get totalPrixReel(): number {
    return this.giftsFollowed.map(g => {
    if(g.partage){
      return g.partage.montant;
    }
    return g.delivery?.prixReel ?? 0;
  })
    .reduce((acc, val) => acc + val, 0);

  }

  onGiftClicked(gift: GiftFollowed): void {
    this.router.navigate(['/dashboard/cadeau', gift.gift.id], {
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
        rawValue = giftFollowed.delivery?.prixReel;
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
}
