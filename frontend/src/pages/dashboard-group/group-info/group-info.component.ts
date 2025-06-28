import {Component, Input, OnInit} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {ErrorService} from 'src/core/services/error.service';
import {CommonModule} from '@angular/common';
import {FormsModule} from '@angular/forms';
import {GroupResume} from 'src/core/models/group/group-resume.model';
import {GroupDTO} from 'src/core/models/group/groupe-dto.model';

@Component({
  selector: 'app-group-info',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
  ],
  templateUrl: './group-info.component.html',
  styleUrl: './group-info.component.scss'
})
export class GroupInfoComponent implements OnInit{

  @Input()
  groupId: number | undefined;
  currentGroup: GroupResume | undefined;
  showModal: boolean = false;
  nomGroupe: string = "";
  description: string = "";

  constructor( private groupService: GroupService,
               private errorService: ErrorService) {
  }

  async ngOnInit() {
    if(this.groupId){
      await this.loadGroup();
    } else {
      this.errorService.showError("Impossible de récupérer le groupe, veuillez vous reconnecter.")
    }

  }

  modify() {
    this.showModal = true;
  }

  async confirmGroupinfo() {
    const group: GroupDTO = {
      nomGroupe: this.nomGroupe,
      description: this.description
    }
    const result = await this.groupService.updateGroup(group, this.groupId!);

    if(result.success){
      await this.loadGroup();
    } else {
      this.errorService.showError(result.message);
    }

    this.showModal = false;
  }

  cancel() {
    this.nomGroupe = this.currentGroup!.nomGroupe;
    this.description = this.currentGroup!.description;
    this.showModal = false;
  }

  async loadGroup(){
    const result = await this.groupService.getGroup( this.groupId!);

    if(result.success){
      this.currentGroup = result.data;
      this.nomGroupe = this.currentGroup!.nomGroupe;
      this.description = this.currentGroup!.description;
    } else {
      this.errorService.showError(result.message);
    }
  }
}
