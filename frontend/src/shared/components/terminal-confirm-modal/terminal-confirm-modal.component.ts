import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-terminal-confirm-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './terminal-confirm-modal.component.html',
  styleUrl: './terminal-confirm-modal.component.scss'
})
export class TerminalConfirmModalComponent {
  @Input() message: string = "Êtes-vous sûr(e) ?";
  @Output() confirm = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();
}
