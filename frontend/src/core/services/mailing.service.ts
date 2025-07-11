import {Injectable} from '@angular/core';
import {ApiResponse} from 'src/core/models/api-response.model';
import {firstValueFrom} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {environment} from 'src/environments/environment';
import {InviteRequest} from 'src/core/models/mailing/invite-request.model';
import {FeedbackRequest} from 'src/core/models/mailing/feedback-request.model';

@Injectable({providedIn: 'root'})
export class MailingService {

  private apiUrl = environment.backendBaseUrl + environment.api.email;
  constructor(private http: HttpClient) {
  }

  async sendFeedbackMail(feedbackRequest: FeedbackRequest): Promise<ApiResponse<void>> {
    const url = `${this.apiUrl}/feedback`;
    try {
      await firstValueFrom(
        this.http.post<void>(url, feedbackRequest)
      );
      return {success: true, data: undefined};

    } catch (error) {
      console.error('[MailingService] Erreur lors de l\'envoi du feedback', error);
      return {success: false, message: "❌ Erreur lors de l\'envoi du feedback."};
    }
  }

  async sendinvitesMail(inviteRequest: InviteRequest): Promise<ApiResponse<void>> {
    const url = `${this.apiUrl}/invitation`;
    try {
      await firstValueFrom(
        this.http.post<void>(url, inviteRequest)
      );
      return {success: true, data: undefined};

    } catch (error) {
      console.error('[MailingService] Erreur lors de l\'envoi des invitations', error);
      return {success: false, message: "❌ Erreur lors de l\'envoi des invitations."};
    }
  }
}
