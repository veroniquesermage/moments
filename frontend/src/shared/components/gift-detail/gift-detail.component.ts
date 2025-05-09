import {Component, Input, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Gift} from 'src/core/models/gift.model';
import {GiftService} from 'src/core/services/gift.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-gift-detail',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './gift-detail.component.html',
  styleUrl: './gift-detail.component.scss'
})
export class GiftDetailComponent implements OnInit{

  @Input() id!: number;
  @Input() context: 'own' | 'other' = 'own';

  gift: Gift | undefined = undefined;

  displayedColumns = [
    { key: 'nom', label: 'Nom' },
    { key: 'description', label: 'Description' },
    { key: 'url', label: 'Url' },
    { key: 'quantite', label: 'Quantité' },
    { key: 'prix', label: 'Prix (€)', formatFn: (v: number) => `${v} €` },
    { key: 'commentaire', label: 'Commentaire' },
    { key: 'priorite', label: 'Priorité' }
  ];

  displayedColumnsMembers = [
    { key: 'nom', label: 'Nom' },
    { key: 'description', label: 'Description' },
    { key: 'url', label: 'Url' },
    { key: 'quantite', label: 'Quantité' },
    { key: 'prix', label: 'Prix (€)', formatFn: (v: number) => `${v} €` },
    { key: 'commentaire', label: 'Commentaire' },
    { key: 'priorite', label: 'Priorité' },
    { key: 'statut', label: 'Statut' },
    { key: 'reserveParId', label: 'Réservé par' }
  ];

  constructor(public giftService: GiftService,
              public router : Router) {
  }

  async ngOnInit(): Promise<void> {
    const result = await this.giftService.getGift(this.id);
    if (result.success) {
      this.gift = result.data;
    }
  }

  retour() {
    this.router.navigate(['/dashboard/mes-cadeaux']);
  }
}
