import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { TerminalModalComponent } from 'src/shared/components/terminal-modal/terminal-modal.component';
import { ErrorService } from 'src/core/services/error.service';
import { GroupService } from 'src/core/services/group.service';
import { InvitationResponse } from 'src/core/models/invitation/invitation-response.model';

@Component({
  selector: 'app-pending-invitations',
  imports: [CommonModule, TerminalModalComponent],
  templateUrl: './pending-invitations.component.html',
  styleUrl: './pending-invitations.component.scss'
})
export class PendingInvitationsComponent {
  @Input() groupId!: number;

  invitations: InvitationResponse[] = [];
  isLoading = false;
  showModal = false;

  constructor(
    private groupService: GroupService,
    public errorService: ErrorService
  ) {}

  async loadInvitations() {
    if (!this.groupId) return;

    this.isLoading = true;
    try {
      const result = await this.groupService.getPendingInvitations(this.groupId);
      if (result.success && result.data) {
        this.invitations = result.data;
      } else {
        this.errorService.showError("❌ Erreur lors du chargement des invitations");
      }
    } catch (error) {
      this.errorService.showError("❌ Erreur lors du chargement des invitations");
    } finally {
      this.isLoading = false;
    }
  }

  async openModal() {
    this.showModal = true;
    await this.loadInvitations();
  }

  closeModal() {
    this.showModal = false;
  }

  getStatusIcon(statut: string): string {
    return statut === 'EN_ATTENTE' ? '⏳' : '❌';
  }

  getStatusText(statut: string): string {
    return statut === 'EN_ATTENTE' ? 'En attente' : 'Expirée';
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
}
