import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ToastrService } from 'src/core/services/toastr.service';

@Component({
  selector: 'app-global-footer',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './global-footer.component.html',
  styleUrl: './global-footer.component.scss'
})
export class GlobalFooterComponent {

  constructor(private toastr: ToastrService) {}

  async copyEmail(event: Event) {
    const email = 'app.moments.ep@gmail.com';
    try {
      await navigator.clipboard.writeText(email);
      this.toastr.show({ message: 'Adresse copiée dans le presse-papiers', type: 'success' });
    } catch (err) {
      console.error('Failed to copy email', err);
    }
  }
}
