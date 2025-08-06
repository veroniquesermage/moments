import {Injectable, signal} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {environment} from 'src/environments/environment';
import {firstValueFrom} from 'rxjs';
import {Result} from 'src/core/models/result.model';
import {ApiResponse} from 'src/core/models/api-response.model';
import {GroupContextService} from 'src/core/services/group-context.service';
import {GroupResume} from 'src/core/models/group/group-resume.model';
import {GroupDTO} from 'src/core/models/group/groupe-dto.model';
import {GroupDetail} from 'src/core/models/group/group-detail.model';

@Injectable({providedIn: 'root'})
export class GroupService {
  private apiUrl = environment.backendBaseUrl + environment.api.groupes;

  groupes = signal<GroupResume[]>([]);
  isLoading = signal<boolean>(false);

  constructor(private http: HttpClient,
              private groupContextService: GroupContextService) {
  }

  async fetchGroups(): Promise<ApiResponse<GroupResume[]>> {
    this.isLoading.set(true);

    try {
      this.isLoading.set(true);
      const groupes = await firstValueFrom(this.http.get<GroupResume[]>(this.apiUrl));
      this.groupes.set(groupes);
      return {success: true, data: groupes};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la récupération des groupes', error);
      return {success: false, message: "❌ Aucun groupe trouvé."};
    } finally {
      this.isLoading.set(false);
    }
  }

  async createGroup(groupDTO: GroupDTO): Promise<ApiResponse<GroupResume>> {
    try {
      const groupeCreated = await firstValueFrom(this.http.post<GroupResume>(this.apiUrl, groupDTO));
      await this.groupContextService.setGroupContext(groupeCreated.id);
      return {success: true, data: groupeCreated};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la création du groupe', error);
      return {success: false, message: "❌ Code invalide ou groupe introuvable."};
    }
  }

  async joinGroup(code: string): Promise<ApiResponse<GroupResume>> {
    try {
      const codeEnc = encodeURIComponent(code);
      const url = `${this.apiUrl + environment.api.rejoindre}/${codeEnc}`;

      const groupeJoined = await firstValueFrom(this.http.post<GroupResume>(url, {}));
      await this.groupContextService.setGroupContext(groupeJoined.id);
      return {success: true, data: groupeJoined};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la création du groupe', error);
      return {success: false, message: "❌ Code invalide ou groupe inexistant."};
    }
  }

  async getGroup(groupId: number): Promise<ApiResponse<GroupResume>> {
    const codeEnc = encodeURIComponent(groupId);
    const url = `${this.apiUrl}/${codeEnc}`;
    try {
      const result = await firstValueFrom(this.http.get<GroupResume>(url));
      return {success: true, data: result};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la récupération du groupe', error);
      return {success: false, message: "❌ Aucun groupe trouvé."};
    }
  }

  async getGroupDetail(groupId: number): Promise<ApiResponse<GroupDetail>> {
    const codeEnc = encodeURIComponent(groupId);
    const url = `${this.apiUrl}/${codeEnc}/details`;
    try {
      const result = await firstValueFrom(this.http.get<GroupDetail>(url));
      return {success: true, data: result};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la récupération du groupe', error);
      return {success: false, message: "❌ Aucun groupe trouvé."};
    }

  }

  async updateGroup(group: GroupDTO, groupId: number): Promise<ApiResponse<GroupResume>> {
    const codeEnc = encodeURIComponent(groupId);
    const url = `${this.apiUrl}/${codeEnc}`;
    try {
      const result = await firstValueFrom(this.http.patch<GroupResume>(url,group));
      return {success: true, data: result};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la mise à jour du groupe', error);
      return {success: false, message: "❌ Impossible de mettre à jour le groupe. veuillez réessayer."};
    }
  }

  async deleteGroup(groupId: number): Promise<ApiResponse<any>> {
    const codeEnc = encodeURIComponent(groupId);
    const url = `${this.apiUrl}/${codeEnc}`;
    try {
      const result = await firstValueFrom(this.http.delete<GroupDetail>(url));
      return {success: true, data: result};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la suppression du groupe', error);
      return {success: false, message: "❌ Suppression impossible. Veuillez réessayer plus tard."};
    }

  }

  async regenererCodeInvitation(groupId: number): Promise<ApiResponse<any>> {
    const codeEnc = encodeURIComponent(groupId);
    const url = `${this.apiUrl}/${codeEnc}/code-invitation`;
    try {
      await firstValueFrom(this.http.patch<void>(url, {}));
      return {success: true, data: 'ok'};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la suppression du groupe', error);
      return {success: false, message: "❌ Suppression impossible. Veuillez réessayer plus tard."};
    }
  }

  loadGroupesIfEmpty(): Promise<Result<GroupResume[]>> {
    if (this.groupes().length > 0) {
      return Promise.resolve({success: true, data: this.groupes()});
    }
    return this.fetchGroups();
  }
}
