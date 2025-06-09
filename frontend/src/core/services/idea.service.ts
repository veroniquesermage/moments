import {Injectable} from '@angular/core';
import {environment} from 'src/environments/environment';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {GroupContextService} from 'src/core/services/group-context.service';
import {ApiResponse} from 'src/core/models/api-response.model';
import {firstValueFrom} from 'rxjs';
import {GiftIdeasResponse} from 'src/core/models/gift/gift-ideas-response.model';
import {GiftIdeaCreate} from 'src/core/models/gift/gift-idea-create.model';


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

  async createIdeas(giftIdeaCreate: GiftIdeaCreate): Promise<ApiResponse<GiftIdeasResponse>> {
    try {
      const giftIdeaResponse = await firstValueFrom(this.http.post<GiftIdeasResponse>(this.apiUrl, giftIdeaCreate, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));

      return {success: true, data: giftIdeaResponse};

    } catch (error) {
      console.error('[IdeaService] Erreur lors de la création de l\'idée', error);

      return {success: false, message: "❌ Impossible de créer le  l\'idée."};
    }
  }

  async deleteIdea(ideaId: number) : Promise<ApiResponse<any>>{
    const idEnc = encodeURIComponent(ideaId);
    const url = `${this.apiUrl}/${idEnc}`;

    try {
      await firstValueFrom(this.http.delete<void>(url,{
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      return {success: true, data: 'ok' };
    } catch (error) {
      console.error('[IdeaService] Erreur lors de la suppression de l\'idée', error);
      return {success: false, message: "❌ Impossible de supprimer l'idée."};
    }
  }

  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('jwt')}`
    });
  }
}
