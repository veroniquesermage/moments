import {Component, EventEmitter, Input, Output} from '@angular/core';
import {CommonModule} from '@angular/common';
import {InviteResponse} from 'src/core/models/mailing/invite-response.model';
import {TerminalModalComponent} from '../terminal-modal/terminal-modal.component';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';

@Component({
  selector: 'app-invitation-recap-modal',
  standalone: true,
  imports: [CommonModule, TerminalModalComponent],
  templateUrl: './invitation-recap-modal.component.html',
  styleUrl: './invitation-recap-modal.component.scss'
})
export class InvitationRecapModalComponent {
  @Input() isVisible: boolean = false;
  @Input() inviteResponse: InviteResponse | null = null;
  @Output() close = new EventEmitter<void>();

  actions: TerminalModalAction[] = [
    {
      label: 'Fermer',
      eventName: 'close',
      style: 'primary'
    }
  ];

  onActionClicked(eventName: string) {
    if (eventName === 'close') {
      this.close.emit();
    }
  }
}