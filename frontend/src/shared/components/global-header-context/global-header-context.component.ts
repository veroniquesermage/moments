import {AfterViewInit, Component, computed, effect, ElementRef, EventEmitter, Output, ViewChild} from '@angular/core';
import {ContextBannerService} from 'src/core/services/context-banner.service';
import {NgIf} from '@angular/common';

@Component({
  selector: 'app-global-header-context',
  standalone: true,
  imports: [
    NgIf
  ],
  templateUrl: './global-header-context.component.html',
  styleUrl: './global-header-context.component.scss'
})
export class GlobalHeaderContextComponent implements AfterViewInit {
  message = computed(() => this.bannerService.message());

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
