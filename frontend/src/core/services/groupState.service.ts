import {Injectable, signal} from '@angular/core';
import {GroupeResume} from 'src/core/models/group-resume.model';

@Injectable({providedIn: 'root'})
export class GroupStateService {

  public selectedGroup = signal<GroupeResume | null>(null);

  setSelectedGroup(group: GroupeResume) {
    this.selectedGroup.set(group);
  }

  getSelectedGroup(): GroupeResume | null {
    return this.selectedGroup();
  }
}
