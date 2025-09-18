import {Injectable} from '@angular/core';
import {ApiResponse} from 'src/core/models/api-response.model';
import {firstValueFrom} from 'rxjs';
import {HttpClient} from '@angular/common/http';
import {environment} from 'src/environments/environment';
import {InviteRequest} from 'src/core/models/mailing/invite-request.model';
import {InviteResponse} from 'src/core/models/mailing/invite-response.model';

@Injectable({providedIn: 'root'})
export class MailingService {

  private apiUrl = environment.backendBaseUrl + environment.api.email;
  constructor(private http: HttpClient) {
  }

  async sendinvitesMail(inviteRequest: InviteRequest): Promise<ApiResponse<InviteResponse>> {
    const url = `${this.apiUrl}/invitation`;
    try {
      const response = await firstValueFrom(
        this.http.post<InviteResponse>(url, inviteRequest)
      );
      return {success: true, data: response};

    } catch (error) {
      console.error('[MailingService] Erreur lors de l\'envoi des invitations', error);
      return {success: false, message: "❌ Erreur lors de l\'envoi des invitations."};
    }
  }
}
