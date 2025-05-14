import {Injectable, signal} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {environment} from 'src/environments/environment';
import {firstValueFrom} from 'rxjs';
import {User} from 'src/security/model/user.model';
import {ApiResponse} from 'src/core/models/api-response.model';

@Injectable({providedIn: 'root'})
export class UserGroupService {

  private apiUrl = environment.backendBaseUrl + environment.api.utilisateur;
  private selectedMemberId = signal<number | null>(null);
  users = signal<User[]>([])

  constructor(private http: HttpClient,) {
  }

  async fetchUserGroup(idGroup: number): Promise<ApiResponse<User[]>> {
    try {
      const url = `${this.apiUrl + environment.api.groupes}/${idGroup}`;
      const users = await firstValueFrom(this.http.get<User[]>(url, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      this.users.set(users);
      return {success: true, data: users};
    } catch (error) {
      console.error('[UserGroupService] Erreur lors de la récupération des membres du groupe', error);
      return {success: false, message: "❌ Groupe inexistant."};
    }
  }

  setSelectedMemberId(id: number | null) {
    this.selectedMemberId.set(id);
  }

  getSelectedMemberId(): number | null {
    return this.selectedMemberId();
  }

  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('jwt')}`
    });
  }

}
