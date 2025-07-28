import {Injectable} from '@angular/core';
import {HttpClient, HttpParams} from '@angular/common/http';
import {environment} from 'src/environments/environment';
import {firstValueFrom} from 'rxjs';
import {ApiResponse} from 'src/core/models/api-response.model';
import {UserDisplay} from 'src/core/models/user-display.model';
import {ExportManagedAccountRequest} from 'src/core/models/export-managed-account-request.model';

@Injectable({providedIn: 'root'})
export class UserGroupService {

  private apiUrl = environment.backendBaseUrl + environment.api.utilisateurGroupe;

  constructor(private http: HttpClient,) {
  }

  async updateNickname(groupId: number, nickname: string): Promise<ApiResponse<any>> {
    const url = `${ this.apiUrl}/${groupId}/surnom`;
    try{
      await firstValueFrom(this.http.patch(url, {nickname}));
      return {success: true, data: 'ok'}
    } catch (error){
      console.error('[UserGroupService] Erreur lors de la mise à jour du surnom', error);
      return {success: false, message: "❌ Erreur lors de la mise à jour du surnom."};
    }
  }

  async deleteUserInGroup(groupId: number, userId?: number): Promise<ApiResponse<any>> {
    const url = `${ this.apiUrl}/${groupId}`;

    let params = new HttpParams();
    if (userId != null) {
      params = params.set('userId', userId.toString());
    }

    try{
      await firstValueFrom(this.http.delete(url, {
        params: params
      }));
      return {success: true, data: 'ok'}
    } catch (error){
      console.error('[UserGroupService] Erreur lors de la suppression de l\'utilisateur dans le groupe', error);
      return {success: false, message: "❌ Erreur lors de la suppression de l\'utilisateur dans le groupe."};
    }
  }

  async updateRoleUsers(groupId: number, rolesUpdate: UserDisplay[]): Promise<ApiResponse<UserDisplay[]>> {
    const url = `${ this.apiUrl}/${groupId}/update`;
    try {
      const result = await firstValueFrom(this.http.patch<UserDisplay[]>(url, rolesUpdate));
      return {success: true, data: result};
    } catch (error) {
      console.error('[UserGroupService] Erreur lors de la mise à jour des rôles', error);
      return {success: false, message: "❌ Impossible de mettre à jour les rôles. Veuillez réessayer."};
    }
  }

  async removeTiersFromGroup(userId: number): Promise<ApiResponse<void>> {
    const idEnc = encodeURIComponent(userId);
    const url = `${this.apiUrl}/compte-tiers/${idEnc}`;
    try{
      await firstValueFrom(this.http.delete<void>(url));
      return {success: true, data: undefined}
    } catch (error) {
      console.error('[UserGroupService] Erreur lors de la suppression d\'un compte tiers', error);
      return {success: false, message: "❌ Erreur lors de la suppression d\'un compte tiers."};
    }
  }

  async exportTiersToGroup(request: ExportManagedAccountRequest): Promise<ApiResponse<void>> {
    const url = `${this.apiUrl}/export-compte-tiers`;
    try{
      await firstValueFrom(this.http.post<void>(url, request));
      return {success: true, data: undefined}
    } catch (error) {
      console.error('[UserGroupService] Erreur lors de l\'export d\'un compte tiers', error);
      return {success: false, message: "❌ Erreur lors de l\'export d\'un compte tiers."};
    }
  }
}
