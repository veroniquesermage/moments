import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-global-footer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './global-footer.component.html',
  styleUrl: './global-footer.component.scss'
})
export class GlobalFooterComponent {}
