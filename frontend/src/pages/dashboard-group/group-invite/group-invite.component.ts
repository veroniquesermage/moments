import {Component, EventEmitter, Input, Output} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {MailingService} from 'src/core/services/mailing.service';
import {ErrorService} from 'src/core/services/error.service';
import {InviteRequest} from 'src/core/models/mailing/invite-request.model';
import {InviteResponse} from 'src/core/models/mailing/invite-response.model';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {InvitationRecapModalComponent} from 'src/shared/components/invitation-recap-modal/invitation-recap-modal.component';
import {GroupService} from 'src/core/services/group.service';
import {ToastrService} from 'src/core/services/toastr.service';
import {PendingInvitationsComponent} from 'src/app/pages/dashboard-group/pending-invitations/pending-invitations.component';
import {GroupContextService} from 'src/core/services/group-context.service';

@Component({
  selector: 'app-group-invite',
  standalone: true,
  imports: [
    FormsModule,
    CommonModule,
    TerminalModalComponent,
    InvitationRecapModalComponent,
    PendingInvitationsComponent
  ],
  templateUrl: './group-invite.component.html',
  styleUrl: './group-invite.component.scss'
})
export class GroupInviteComponent {

  @Input()
  groupId: number | undefined;

  @Output()
  membersUpdated = new EventEmitter<void>();
  mails: string = '';

  // Variables pour la modale de recap
  showRecapModal: boolean = false;
  inviteResponse: InviteResponse | null = null;

  constructor(private mailingService: MailingService,
              public errorService: ErrorService,
              private groupeService: GroupService,
              private toastrService: ToastrService,
              private groupContextService: GroupContextService) {
  }

  async sendInvitation() {
    if (!this.mails.trim()) {
      this.errorService.showError('Veuillez saisir au moins une adresse email.');
      return;
    }

    // Nettoyer et transformer les emails en liste
    const emails: string[] = this.mails
      .split(/\r?\n/)
      .map(e => e.trim())
      .filter(e => e.length > 0);

    const inviteRequest: InviteRequest = { emails };
    const result = await this.mailingService.sendinvitesMail(inviteRequest);

    if (!result.success) {
      this.errorService.showError(result.message);
      return;
    }

    // Afficher la modale de recap
    this.inviteResponse = result.data!;
    this.showRecapModal = true;
  }

  async onRecapModalClose() {
    this.showRecapModal = false;

    // Vider le champ emails seulement si des invitations ont été envoyées
    if (this.inviteResponse?.emails_envoyes.length! > 0) {
      this.mails = '';
      // Rafraîchir la liste des membres après envoi d'invitations
      this.membersUpdated.emit();
    }

    this.inviteResponse = null;
  }

  normalizeMails() {
    // Transforme les virgules et les multiples espaces en retour à la ligne
    this.mails = this.mails
      .replace(/[,\s]+/g, '\n')           // Tout séparateur devient un \n
      .replace(/\n{2,}/g, '\n')           // Supprime les lignes vides multiples
      .trim();                            // Nettoie début/fin
  }


}
