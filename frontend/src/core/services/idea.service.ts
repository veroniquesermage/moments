import {Injectable} from '@angular/core';
import {environment} from 'src/environments/environment';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {GroupContextService} from 'src/core/services/group-context.service';
import {ApiResponse} from 'src/core/models/api-response.model';
import {firstValueFrom} from 'rxjs';
import {GiftIdeasResponse} from 'src/core/models/gift/gift-ideas-response.model';


@Injectable({providedIn: 'root'})
export class IdeaService {

  private apiUrl = environment.backendBaseUrl + environment.api.idees;

  constructor(private http: HttpClient,
              private groupContextService: GroupContextService) {
  }

  async fetchIdeas(): Promise<ApiResponse<GiftIdeasResponse[]>> {
    const groupId = this.groupContextService.getGroupId();
    const idEnc = encodeURIComponent(groupId);
    const url = `${this.apiUrl}/${idEnc}`;
    try {
      const ideas = await firstValueFrom(this.http.get<GiftIdeasResponse[]>(url, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      return {success: true, data: ideas};
    } catch (error) {
      console.error('[IdeaService] Erreur lors de la récupération des idées', error);
      return {success: false, message: "❌ Aucune idée trouvée."};
    }
  }


  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('jwt')}`
    });
  }


}
