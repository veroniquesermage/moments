import { AfterViewInit, Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ContextBannerService } from 'src/core/services/context-banner.service';
import { effect } from '@angular/core';

@Component({
  selector: 'app-global-header-context',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './global-header-context.component.html',
  styleUrl: './global-header-context.component.scss'
})
export class GlobalHeaderContextComponent implements AfterViewInit {
  message = this.bannerService.message;

  @ViewChild('banner') bannerRef?: ElementRef<HTMLDivElement>;
  @Output() heightChange = new EventEmitter<number>();

  constructor(private bannerService: ContextBannerService) {}

  ngAfterViewInit() {
    effect(() => {
      const msg = this.message();
      setTimeout(() => {
        const h = msg && this.bannerRef ? this.bannerRef.nativeElement.offsetHeight : 0;
        this.heightChange.emit(h);
      });
    });
  }
}
