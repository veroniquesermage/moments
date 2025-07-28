import {AfterViewInit, Component, effect, ElementRef, EventEmitter, Output, Signal, ViewChild} from '@angular/core';
import {CommonModule} from '@angular/common';
import {Toast, ToastrService} from 'src/core/services/toastr.service';

@Component({
  selector: 'app-global-toastr',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './global-toastr.component.html',
  styleUrl: './global-toastr.component.scss'
})
export class GlobalToastrComponent implements AfterViewInit {


  @ViewChild('container') containerRef?: ElementRef<HTMLDivElement>;
  @Output() heightChange = new EventEmitter<number>();
  toasts: Signal<Toast[]>;

  constructor(private toastrService: ToastrService) {
    this.toasts = this.toastrService.toastsSignal();
  }

  ngAfterViewInit() {
    effect(() => {
      setTimeout(() => {
        const height = this.containerRef?.nativeElement.offsetHeight ?? 0;
        this.heightChange.emit(height);
      });
    });
  }
}
