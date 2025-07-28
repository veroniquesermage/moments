import {Component, Input} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {MailingService} from 'src/core/services/mailing.service';
import {ErrorService} from 'src/core/services/error.service';
import {InviteRequest} from 'src/core/models/mailing/invite-request.model';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {GroupService} from 'src/core/services/group.service';
import {ToastrService} from 'src/core/services/toastr.service';

@Component({
  selector: 'app-group-invite',
  standalone: true,
  imports: [
    FormsModule,
    CommonModule,
    TerminalModalComponent
  ],
  templateUrl: './group-invite.component.html',
  styleUrl: './group-invite.component.scss'
})
export class GroupInviteComponent {

  @Input()
  groupId: number | undefined;
  mails: string = '';
  validMails: InviteRequest = { emails: [] };
  invalidMails: string[] = [];

  constructor(private mailingService: MailingService,
              public errorService: ErrorService,
              private groupeService: GroupService,
              private toastrService: ToastrService) {
  }

  private isValidEmail(email: string): boolean {
    // Regex simple, pas parano, mais efficace
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email.trim());
  }

  checkMail() {
    this.validMails.emails = [];
    this.invalidMails = [];
    const emails: string[] = this.mails
      .split(/\r?\n/)
      .map(e => e.trim())
      .filter(e => e.length > 0);

    for (const email of emails) {
      if (this.isValidEmail(email)) {
        this.validMails.emails.push(email);
      } else {
        this.invalidMails.push(email);
      }
    }
  }

  async sendInvitation() {
    const result = await this.mailingService.sendinvitesMail(this.validMails!);

    if (!result.success) {
      this.errorService.showError(result.message);
      return;
    }

    this.mails = '';
    this.validMails = {emails: []} ;
    this.invalidMails = [];
  }

  normalizeMails() {
    // Transforme les virgules et les multiples espaces en retour à la ligne
    this.mails = this.mails
      .replace(/[,\s]+/g, '\n')           // Tout séparateur devient un \n
      .replace(/\n{2,}/g, '\n')           // Supprime les lignes vides multiples
      .trim();                            // Nettoie début/fin
  }


  async refreshInviteCode() {

    if (!this.groupId) {
      this.errorService.showError('Veuillez réessayer plus tard.');
      return;
    }
    const result = await this.groupeService.regenererCodeInvitation(this.groupId);
    if(result.success){
      this.toastrService.show({ message: "Le code d'invitation du groupe a bien été modifié 👍", type: 'success' });
    } else {
      this.errorService.showError('Veuillez réessayer plus tard.');
    }
  }
}
