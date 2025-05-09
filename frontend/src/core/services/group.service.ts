import {Injectable, signal} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {environment} from 'src/environments/environment';
import {GroupeResume} from 'src/core/models/group-resume.model';
import {firstValueFrom} from 'rxjs';
import {GroupStateService} from 'src/core/services/groupState.service';
import {GroupeDTO} from 'src/core/models/groupe-dto.model';
import {Result} from 'src/core/models/result.model';

@Injectable({providedIn: 'root'})
export class GroupService {
  private apiUrl = environment.backendBaseUrl + environment.api.groupes;

  groupes = signal<GroupeResume[]>([]);
  selectedGroup = signal<GroupeResume | null>(null);
  errorMessage: string | null = null;
  isLoading = signal<boolean>(false);

  constructor(private http: HttpClient,
              private groupStateService: GroupStateService) {
  }

  async fetchGroups(): Promise<Result<GroupeResume[]>> {
    this.isLoading.set(true);

    try {
      this.isLoading.set(true);
      const groupes = await firstValueFrom(this.http.get<GroupeResume[]>(this.apiUrl, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      this.groupes.set(groupes);
      return {success: true, data: groupes};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la récupération des groupes', error);
      return {success: false, message: "❌ Aucun groupe trouvé."};
    } finally {
      this.isLoading.set(false);
    }
  }

  async createGroup(groupDTO: GroupeDTO) {
    try {
      const groupeCreated = await firstValueFrom(this.http.post<GroupeResume>(this.apiUrl, groupDTO, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      this.groupStateService.setSelectedGroup(groupeCreated);
      return {success: true, data: groupeCreated};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la création du groupe', error);
      return {success: false, message: "❌ Code invalide ou groupe introuvable."};
    }
  }

  async joinGroup(code: string) {
    try {
      const codeEnc = encodeURIComponent(code);
      const url = `${this.apiUrl}/environment.api.rejoindre/${codeEnc}`;

      const groupeJoined = await firstValueFrom(this.http.post<GroupeResume>(url, {}, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      this.groupStateService.setSelectedGroup(groupeJoined);
      return {success: true, data: groupeJoined};
    } catch (error) {
      console.error('[GroupService] Erreur lors de la création du groupe', error);
      return {success: false, message: "❌ Code invalide ou groupe inexistant."};
    }
  }

  loadGroupesIfEmpty(): Promise<Result<GroupeResume[]>> {
    if (this.groupes().length > 0) {
      return Promise.resolve({success: true, data: this.groupes()});
    }
    return this.fetchGroups();
  }

  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('jwt')}`
    });
  }

  setSelectedGroup(group: GroupeResume): void {
    this.selectedGroup.set(group);
  }

  getSelectedGroup(): GroupeResume | null {
    return this.selectedGroup();
  }

  clear(): void {
    this.groupes.set([]);
    this.selectedGroup.set(null);
  }
}
