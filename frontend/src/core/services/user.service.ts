import {Injectable, signal} from '@angular/core';
import {environment} from 'src/environments/environment';
import {HttpClient} from '@angular/common/http';
import {ApiResponse} from 'src/core/models/api-response.model';
import {UserDisplay} from 'src/core/models/user-display.model';
import {firstValueFrom} from 'rxjs';
import {UserTiersRequest} from 'src/core/models/user-tiers-request.model';
import {UserTiersResponse} from 'src/core/models/user-tiers-response.model';

@Injectable({providedIn: 'root'})
export class UserService {

  userTiersResponse = signal<UserTiersResponse[]>([]);
  private apiUrl = environment.backendBaseUrl + environment.api.utilisateur;

  constructor(private http: HttpClient,) {
  }

  async fetchUserGroup(idGroup: number): Promise<ApiResponse<UserDisplay[]>> {
    try {
      const url = `${this.apiUrl + environment.api.groupes}/${idGroup}`;
      const users = await firstValueFrom(this.http.get<UserDisplay[]>(url));
      return {success: true, data: users};
    } catch (error) {
      console.error('[UserGroupService] Erreur lors de la récupération des membres du groupe', error);
      return {success: false, message: "❌ Groupe inexistant."};
    }
  }

  async getUsersWithSharedGroups(): Promise<ApiResponse<UserDisplay[]>> {
    try {
      const url = `${this.apiUrl}/en-commun`;
      const users = await firstValueFrom(this.http.get<UserDisplay[]>(url));
      return {success: true, data: users};
    } catch (error) {
      console.error('[UserGroupService] Erreur lors de la récupération des membres qui partagent un groupe en commun avec l\'utilisateur', error);
      return {success: false, message: "❌ Erreur lors de la récupération des membres qui partagent un groupe en commun avec l\'utilisateur."};
    }
  }

  async createUserTiers(userTiers: UserTiersRequest): Promise<ApiResponse<UserTiersResponse>> {
    const url = `${this.apiUrl}/compte-tiers`;
    try{
      const userTiersResponse = await firstValueFrom(this.http.post<UserTiersResponse>(url, userTiers));
      return {success: true, data: userTiersResponse}
    } catch (error) {
      console.error('[UserService] Erreur lors de la création d\'un compte tiers', error);
      return {success: false, message: "❌ Erreur lors de la création d\'un compte tiers."};
    }
  }

  async getAllUserTiers(): Promise<ApiResponse<UserTiersResponse[]>> {
    const url = `${this.apiUrl}/me/comptes-tiers`;
    try{
      const userTiersResponse = await firstValueFrom(this.http.get<UserTiersResponse[]>(url));
      return {success: true, data: userTiersResponse}
    } catch (error) {
      console.error('[UserService] Erreur lors de la récupération des comptes tiers', error);
      return {success: false, message: "❌ Erreur lors de la création des comptes tiers."};
    }
  }

  async loadAllUserTiers():Promise<boolean>{
    const response = await this.getAllUserTiers()
    if(response.success){
      this.userTiersResponse.set(response.data)
      return true;
    }
    return false;
  }

}
