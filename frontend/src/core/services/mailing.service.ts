import {Injectable} from '@angular/core';
import {ApiResponse} from 'src/core/models/api-response.model';
import {firstValueFrom} from 'rxjs';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {GroupContextService} from 'src/core/services/group-context.service';
import {environment} from 'src/environments/environment';
import {FeedbackRequest} from 'src/core/models/feedback-request.model';

@Injectable({providedIn: 'root'})
export class MailingService {

  private apiUrl = environment.backendBaseUrl + environment.api.email;
  constructor(private http: HttpClient,
              private groupContextService: GroupContextService) {
  }

  async sendFeedbackMail(feedbackRequest: FeedbackRequest): Promise<ApiResponse<void>> {

    try {
      await firstValueFrom(
        this.http.post<void>(this.apiUrl, feedbackRequest, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );
      return {success: true, data: undefined};

    } catch (error) {
      console.error('[MailingService] Erreur lors de l\'envoi du feedback', error);
      return {success: false, message: "❌ Erreur lors de l\'envoi du feedback."};
    }
  }

  private getAuthHeaders(): HttpHeaders {
    const headersConfig: { [key: string]: string } = {
      'Authorization': `Bearer ${localStorage.getItem('app_kdo.jwt')}`
    };

    const currentGroupId = this.groupContextService.getGroupId();
    if (currentGroupId) {
      headersConfig['X-Group-Id'] = currentGroupId.toString();
    }

    return new HttpHeaders(headersConfig);
  }
}
