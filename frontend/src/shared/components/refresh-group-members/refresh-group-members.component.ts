import {Component, EventEmitter, Output} from '@angular/core';
import {GroupContextService} from 'src/core/services/group-context.service';
import {ToastrService} from 'ngx-toastr';

@Component({
  selector: 'app-refresh-group-members',
  standalone: true,
  imports: [],
  templateUrl: './refresh-group-members.component.html',
  styleUrl: './refresh-group-members.component.scss'
})
export class RefreshGroupMembersComponent {

  @Output()
  refreshed = new EventEmitter<void>();
  loading = false;

  constructor(private groupContext: GroupContextService,
              private toastr: ToastrService) {}

  async onRefresh(): Promise<void> {
    this.loading = true;
    try {
      await this.groupContext.refreshMembers();
      this.toastr.success('Membres mis à jour 👍');
    } catch (err) {
      console.error('[RefreshButton] Échec du rafraîchissement', err);
      this.toastr.error('Échec du rafraîchissement des membres 😕');
    } finally {
      this.loading = false;
      this.refreshed.emit();
    }
  }
}
