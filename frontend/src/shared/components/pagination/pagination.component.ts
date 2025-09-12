import { Component, Input, Output, EventEmitter, inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ResponsiveService } from '../../../core/services/responsive.service';
import { PaginationInfo } from '../../../core/models/common/pagination.model';

@Component({
  selector: 'app-pagination',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="pagination-container" *ngIf="paginationInfo && paginationInfo.total_pages > 1">
      
      <!-- Version mobile : navigation simple -->
      <div class="mobile-pagination" *ngIf="isMobile()">
        <button 
          class="btn-pagination" 
          [disabled]="!paginationInfo.has_previous" 
          (click)="previousPage()">
          ‹ Précédent
        </button>
        
        <span class="page-info">
          {{ paginationInfo.page }} / {{ paginationInfo.total_pages }}
        </span>
        
        <button 
          class="btn-pagination" 
          [disabled]="!paginationInfo.has_next" 
          (click)="nextPage()">
          Suivant ›
        </button>
      </div>

      <!-- Version desktop : pagination complète -->
      <div class="desktop-pagination" *ngIf="!isMobile()">
        <button 
          class="btn-pagination" 
          [disabled]="!paginationInfo.has_previous" 
          (click)="previousPage()">
          ‹ Précédent
        </button>

        <div class="page-numbers">
          <button 
            *ngFor="let page of getVisiblePages()" 
            class="btn-page-number"
            [class.active]="page === paginationInfo.page"
            (click)="goToPage(page)">
            {{ page }}
          </button>
        </div>

        <button 
          class="btn-pagination" 
          [disabled]="!paginationInfo.has_next" 
          (click)="nextPage()">
          Suivant ›
        </button>
      </div>

      <!-- Info totale -->
      <div class="pagination-info" *ngIf="showInfo">
        {{ paginationInfo.total_count }} éléments au total
      </div>
    </div>
  `,
  styleUrls: ['./pagination.component.scss']
})
export class PaginationComponent {
  @Input() paginationInfo!: PaginationInfo;
  @Input() showInfo: boolean = true;
  @Output() pageChange = new EventEmitter<number>();

  private responsiveService = inject(ResponsiveService);
  
  isMobile = this.responsiveService.isMobile;

  previousPage() {
    if (this.paginationInfo.has_previous) {
      this.pageChange.emit(this.paginationInfo.page - 1);
    }
  }

  nextPage() {
    if (this.paginationInfo.has_next) {
      this.pageChange.emit(this.paginationInfo.page + 1);
    }
  }

  goToPage(page: number) {
    if (page !== this.paginationInfo.page) {
      this.pageChange.emit(page);
    }
  }

  getVisiblePages(): number[] {
    const current = this.paginationInfo.page;
    const total = this.paginationInfo.total_pages;
    const delta = 2;
    
    const range = [];
    const rangeStart = Math.max(1, current - delta);
    const rangeEnd = Math.min(total, current + delta);
    
    for (let i = rangeStart; i <= rangeEnd; i++) {
      range.push(i);
    }
    
    return range;
  }
}