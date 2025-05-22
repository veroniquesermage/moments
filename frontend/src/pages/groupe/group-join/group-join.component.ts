import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';

@Component({
  selector: 'app-group-join',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, TerminalModalComponent],
  templateUrl: './group-join.component.html',
  styleUrl: './group-join.component.scss'
})
export class GroupJoinComponent {

  groupeForm: FormGroup;

  constructor(private fb: FormBuilder,
              private groupeService: GroupService,
              public router: Router,
              public errorService: ErrorService) {
    this.groupeForm = this.fb.group({
      code: ['', Validators.required]
    })
  }

  async onSubmit() {
    if (this.groupeForm.valid) {
      let value = this.groupeForm.value;
      const result = await this.groupeService.joinGroup(value.code);

      if (result.success) {
        await this.router.navigate(['/dashboard']);
      } else {
        this.errorService.showError(result.message);
      }

    } else {
      console.warn('❌ Formulaire invalide');
      this.errorService.showError('❌ Formulaire invalide');
    }
  }
}
