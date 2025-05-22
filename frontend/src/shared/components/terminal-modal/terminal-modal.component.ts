import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';

@Component({
  selector: 'app-terminal-modal',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './terminal-modal.component.html',
  styleUrl: './terminal-modal.component.scss'
})
export class TerminalModalComponent {
  @Input() message: string = "Êtes-vous sûr(e) ?";
  @Input() actions: TerminalModalAction[] = [];
  @Output() actionClicked = new EventEmitter<string>();
}
