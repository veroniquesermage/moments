import {Injectable, signal} from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {environment} from 'src/environments/environment';
import {GroupeResume} from 'src/core/models/groupe-resume.model';
import {firstValueFrom} from 'rxjs';

@Injectable({providedIn: 'root'})
export class GroupService {
  private apiUrl = environment.backendBaseUrl + environment.api.groupes;

  groupes = signal<GroupeResume[]>([]);
  selectedGroup = signal<GroupeResume | null>(null);

  constructor(private http: HttpClient) {
  }

  async fetchGroups(): Promise<GroupeResume[]> {
    try {
      const groupes = await firstValueFrom(this.http.get<GroupeResume[]>(this.apiUrl, {
        headers: new HttpHeaders({
          'Authorization': `Bearer ${localStorage.getItem('jwt')}`
        })
      }));
      this.groupes.set(groupes);
      return groupes;
    } catch (error) {
      console.error('[GroupService] Erreur lors de la récupération des groupes', error);
      return [];
    }
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
