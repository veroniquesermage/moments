import {Injectable, signal} from '@angular/core';
import {GroupResume} from 'src/core/models/group-resume.model';

@Injectable({providedIn: 'root'})
export class GroupStateService {

  public selectedGroup = signal<GroupResume | null>(null);

  setSelectedGroup(group: GroupResume) {
    this.selectedGroup.set(group);
  }

  getSelectedGroup(): GroupResume | null {
    return this.selectedGroup();
  }
}
