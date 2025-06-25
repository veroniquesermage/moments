import {Component, Input, ViewEncapsulation} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {MailingService} from 'src/core/services/mailing.service';
import {QuillModule} from 'ngx-quill';
import {FeedbackRequest} from 'src/core/models/mailing/feedback-request.model';


@Component({
  selector: 'app-feedback-test',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    QuillModule
  ],
  templateUrl: './feedback-test.component.html',
  styleUrl: './feedback-test.component.scss',
  encapsulation: ViewEncapsulation.None,
})
export class FeedbackTestComponent {

  @Input()
  composant: string = '';
  showFeedbackModal: boolean = false;
  commentaire: string = "";
  editorModules = {
    toolbar: [
      ['bold', 'italic', 'underline'],
      [{ 'list': 'ordered'}, { 'list': 'bullet' }],
    ],
  };
  placeholder: string = 'Ecrire votre commentaire ici...'


  constructor(private mailingService: MailingService) {
  }

  clickOn() {
    this.showFeedbackModal = true;
  }


  cancelTemporary() {
    this.showFeedbackModal = false;
  }

  async sendFeedback() {
    const feedbackRequest: FeedbackRequest = {
      composant: this.composant,
      commentaire: this.commentaire
    }
    await this.mailingService.sendFeedbackMail(feedbackRequest);
    this.clear();
  }

  clear() {
    this.commentaire = '';
    this.showFeedbackModal = false;
  }
}
