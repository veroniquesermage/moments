import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-terminal-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './terminal-modal.component.html',
  styleUrl: './terminal-modal.component.scss'
})
export class TerminalModalComponent {
  @Input() message: string = "Êtes-vous sûr(e) ?";

  @Input() mode: 'confirm' | 'error' = 'confirm';
  @Output() confirm = new EventEmitter<void>();
  @Output() cancel = new EventEmitter<void>();
  @Output() close  = new EventEmitter<void>();

}
