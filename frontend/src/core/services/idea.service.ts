import {Injectable} from '@angular/core';
import {environment} from 'src/environments/environment';
import {HttpClient} from '@angular/common/http';
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
      const ideas = await firstValueFrom(this.http.get<GiftIdeasResponse[]>(url));
      return {success: true, data: ideas};
    } catch (error) {
      console.error('[IdeaService] Erreur lors de la récupération des idées', error);
      return {success: false, message: "❌ Aucune idée trouvée."};
    }
  }

  async createIdeas(giftIdeaCreate: GiftIdeaCreate): Promise<ApiResponse<GiftIdeasResponse>> {
    try {
      const giftIdeaResponse = await firstValueFrom(this.http.post<GiftIdeasResponse>(this.apiUrl, giftIdeaCreate));

      return {success: true, data: giftIdeaResponse};

    } catch (error) {
      console.error('[IdeaService] Erreur lors de la création de l\'idée', error);

      return {success: false, message: "❌ Impossible de créer le  l\'idée."};
    }
  }

  async changeVisibility(ideaId: number, visibility: boolean) : Promise<ApiResponse<any>> {
    const idEnc = encodeURIComponent(ideaId);
    const url = `${this.apiUrl}/${idEnc}`;

    try {
      await firstValueFrom(this.http.patch<void>(url, {visibility}));

      return {success: true, data: 'ok' };
    } catch (error) {
      console.error('[IdeaService] Erreur lors du changement de visibilité', error);
      return {success: false, message: "❌ Impossible de changer la visibilité de l'idée."};
    }
  }

  async duplicateIdea(ideaId: number, newDestId: number) : Promise<ApiResponse<GiftIdeasResponse>> {
    const idEnc = encodeURIComponent(ideaId);
    const url = `${this.apiUrl}/${idEnc}`;

    try {
      const result = await firstValueFrom(this.http.post<GiftIdeasResponse>(url, {newDestId}));

      return {success: true, data: result };
    } catch (error) {
      console.error('[IdeaService] Erreur lors de la duplication de l\'idée', error);
      return {success: false, message: "❌ Impossible de dupliquer l'idée."};
    }
  }

  async deleteIdea(ideaId: number) : Promise<ApiResponse<any>>{
    const idEnc = encodeURIComponent(ideaId);
    const url = `${this.apiUrl}/${idEnc}`;

    try {
      await firstValueFrom(this.http.delete<void>(url));
      return {success: true, data: 'ok' };
    } catch (error) {
      console.error('[IdeaService] Erreur lors de la suppression de l\'idée', error);
      return {success: false, message: "❌ Impossible de supprimer l'idée."};
    }
  }
}
