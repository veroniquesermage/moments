import {Component, OnDestroy, OnInit} from '@angular/core';
import {GiftTableComponent} from 'src/shared/components/gift-table/gift-table.component';
import {formatDate, NgIf} from '@angular/common';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {Router} from '@angular/router';
import {GiftService} from 'src/core/services/gift.service';
import {ErrorService} from 'src/core/services/error.service';
import {User} from 'src/security/model/user.model';
import {Subscription} from 'rxjs';
import {ViewportService} from 'src/core/services/viewport.service';
import {ColumnDefinition} from 'src/core/models/column-definition.model';
import {Gift} from 'src/core/models/gift/gift.model';

@Component({
  selector: 'app-my-gifts-follow-up',
  standalone: true,
  imports: [
    GiftTableComponent,
    NgIf,
    TerminalModalComponent
  ],
  templateUrl: './my-gifts-follow-up.component.html',
  styleUrl: './my-gifts-follow-up.component.scss'
})
export class MyGiftsFollowUpComponent implements OnInit, OnDestroy{

  displayedColumns: ColumnDefinition[] = [];
  portraitSub?: Subscription;
  isPortrait = false;


  readonly displayedColumnsPortrait:  ColumnDefinition[] = [
    {key: 'utilisateur', label: 'Destinataire', formatFn: (u: User | null | undefined) => u?.name || '—' },
    { key: 'nom', label: 'Nom' },
    {key: 'prixReel', label: 'Prix réel (€)', formatFn: (v: number | null) => v != null ? `${v}€` : '—'},
    { key: 'statut', label: 'Statut' }
  ];

  readonly displayedColumnsDesktop:  ColumnDefinition[] = [
    {key: 'utilisateur', label: 'Destinataire', formatFn: (u: User | null | undefined) => u?.name || '—' },
    {key: 'nom', label: 'Nom'},
    {key: 'magasin', label: 'Magasin'},
    {key: 'quantite', label: 'Quantité'},
    {key: 'prixReel', label: 'Prix réel (€)', formatFn: (v: number | null) => v != null ? `${v}€` : '—'},
    {key: 'lieuLivraison', label: 'Lieu de livraison'},
    {key: 'dateLivraison', label: 'Date de livraison', formatFn: (v: string) => v ? formatDate(v, 'dd/MM/yyyy', 'fr-FR') : '—'},
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
    if (!result.success) {
      this.errorService.showError(result.message);
    }
  }

  ngOnDestroy(): void {
    this.portraitSub?.unsubscribe();
  }

  get totalPrixReel(): number {
    return this.giftService.gifts()
      .map(g => g.prixReel ?? 0)
      .reduce((acc, val) => acc + val, 0);
  }

  onGiftClicked(gift: Gift): void {
    this.router.navigate(['/dashboard/cadeau', gift.id], {
      queryParams: { context: 'suivi' }
    });
  }

  async retour() {
      await this.router.navigate(['/dashboard']);
  }

  protected readonly Number = Number;
}
