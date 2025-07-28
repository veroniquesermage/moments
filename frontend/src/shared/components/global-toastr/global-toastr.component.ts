import { AfterViewInit, Component, ElementRef, EventEmitter, Output, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastrService } from 'src/core/services/toastr.service';
import { effect } from '@angular/core';

@Component({
  selector: 'app-global-toastr',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './global-toastr.component.html',
  styleUrl: './global-toastr.component.scss'
})
export class GlobalToastrComponent implements AfterViewInit {
  toasts = this.toastrService.toastsSignal();

  @ViewChild('container') containerRef?: ElementRef<HTMLDivElement>;
  @Output() heightChange = new EventEmitter<number>();

  constructor(private toastrService: ToastrService) {}

  ngAfterViewInit() {
    effect(() => {
      setTimeout(() => {
        const height = this.containerRef?.nativeElement.offsetHeight ?? 0;
        this.heightChange.emit(height);
      });
    });
  }
}
