import {Injectable} from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {environment} from 'src/environments/environment';
import {firstValueFrom} from 'rxjs';
import {User} from 'src/security/model/user.model';
import {ApiResponse} from 'src/core/models/api-response.model';
import {UserDisplay} from 'src/core/models/user-display.model';

@Injectable({providedIn: 'root'})
export class UserGroupService {

  private apiUrl = environment.backendBaseUrl + environment.api.utilisateur;

  constructor(private http: HttpClient,) {
  }

  async fetchUserGroup(idGroup: number): Promise<ApiResponse<UserDisplay[]>> {
    try {
      const url = `${this.apiUrl + environment.api.groupes}/${idGroup}`;
      const users = await firstValueFrom(this.http.get<UserDisplay[]>(url, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      return {success: true, data: users};
    } catch (error) {
      console.error('[UserGroupService] Erreur lors de la récupération des membres du groupe', error);
      return {success: false, message: "❌ Groupe inexistant."};
    }
  }

  async getUser(): Promise<ApiResponse<User>> {
    const url = `${this.apiUrl.replace(/\/$/, '')}/me`;
    try {
      const user = await firstValueFrom(this.http.get<User>(url, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      return {success: true, data: user};
    } catch (error) {
      console.error('[UserGroupService] Erreur lors de la récupération de l\'utilisateur', error);
      return {success: false, message: "❌ Aucun membre trouvé."};
    }
  }

  async updateNickname(groupId: number, nickname: string): Promise<ApiResponse<any>> {
    const url = `${ environment.backendBaseUrl + environment.api.utilisateurGroupe}/${groupId}/surnom`;
    try{
      await firstValueFrom(this.http.patch(url, {nickname}, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      return {success: true, data: 'ok'}
    } catch (error){
      console.error('[UserGroupService] Erreur lors de la mise à jour du surnom', error);
      return {success: false, message: "❌ Erreur lors de la mise à jour du surnom."};
    }
  }

  async deleteUserInGroup(groupId: number, userId?: number): Promise<ApiResponse<any>> {
    const url = `${ environment.backendBaseUrl + environment.api.utilisateurGroupe}/${groupId}`;

    let params = new HttpParams();
    if (userId != null) {
      params = params.set('userId', userId.toString());
    }

    try{
      await firstValueFrom(this.http.delete(url, {
        headers: this.getAuthHeaders(),
        params: params,
        withCredentials: true
      }));
      return {success: true, data: 'ok'}
    } catch (error){
      console.error('[UserGroupService] Erreur lors de la suppression de l\'utilisateur dans le groupe', error);
      return {success: false, message: "❌ Erreur lors de la suppression de l\'utilisateur dans le groupe."};
    }
  }

  async updateRoleUsers(groupId: number, rolesUpdate: UserDisplay[]): Promise<ApiResponse<UserDisplay[]>> {
    const url = `${ environment.backendBaseUrl + environment.api.utilisateurGroupe}/${groupId}/update`;
    try {
      const result = await firstValueFrom(this.http.patch<UserDisplay[]>(url, rolesUpdate, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      return {success: true, data: result};
    } catch (error) {
      console.error('[UserGroupService] Erreur lors de la mise à jour des rôles', error);
      return {success: false, message: "❌ Impossible de mettre à jour les rôles. Veuillez réessayer."};
    }
  }

  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('app_kdo.jwt')}`
    });
  }

}
