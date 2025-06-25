import { Component } from '@angular/core';
import {FormsModule} from '@angular/forms';
import {CommonModule} from '@angular/common';
import {MailingService} from 'src/core/services/mailing.service';
import {ErrorService} from 'src/core/services/error.service';
import {InviteRequest} from 'src/core/models/mailing/invite-request.model';

@Component({
  selector: 'app-group-invite',
  standalone: true,
  imports: [
    FormsModule,
    CommonModule
  ],
  templateUrl: './group-invite.component.html',
  styleUrl: './group-invite.component.scss'
})
export class GroupInviteComponent {
  mails: string = '';
  validMails: InviteRequest = { emails: [] };
  invalidMails: string[] = [];

  constructor(private mailingService: MailingService,
              private errorService: ErrorService) {
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


}
