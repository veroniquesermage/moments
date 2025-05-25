import {Component, inject} from '@angular/core';
import {ActivatedRoute, Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {GiftDetailComponent} from 'src/shared/components/detail/gift-detail/gift-detail.component';

@Component({
  selector: 'app-gift-detail-page',
  standalone: true,
  imports: [
    CommonModule,
    GiftDetailComponent
  ],
  templateUrl: './gift-detail-page.component.html',
  styleUrl: './gift-detail-page.component.scss'
})
export class GiftDetailPageComponent {

  private route = inject(ActivatedRoute);
  giftId: number | undefined = undefined;
  context: 'mes-cadeaux' | 'cadeaux-groupe' | 'suivi' | 'idee-cadeau' = 'mes-cadeaux';

  constructor(
    public router: Router) {
    const idParam = this.route.snapshot.paramMap.get('id');
    this.context = this.route.snapshot.data['context'] as 'mes-cadeaux' | 'cadeaux-groupe' | 'suivi' | 'idee-cadeau';
    console.log(this.context);
    this.giftId = idParam ? +idParam : undefined;
  }

  handleBack(): void {
    if (this.context === 'mes-cadeaux') {
      this.router.navigate(['/dashboard/mes-cadeaux']);
    } else if (this.context === 'cadeaux-groupe') {
      this.router.navigate(['/dashboard/leurs-cadeaux']);
    } else if (this.context === 'suivi') {
      this.router.navigate(['/dashboard/cadeaux-suivis']);
    } else {
      this.router.navigate(['/dashboard']);
    }
  }

}
