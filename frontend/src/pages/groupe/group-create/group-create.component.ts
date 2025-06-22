import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {GroupDTO} from 'src/core/models/group/groupe-dto.model';

@Component({
  selector: 'app-group-create',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, TerminalModalComponent, FeedbackTestComponent],
  templateUrl: './group-create.component.html',
  styleUrl: './group-create.component.scss'
})
export class GroupCreateComponent {

  groupeForm: FormGroup;
  composant: string = "GroupCreateComponent";
  constructor(private fb: FormBuilder,
              private groupeService: GroupService,
              public router: Router,
              public errorService: ErrorService) {
    this.groupeForm = this.fb.group({
      nomGroupe: ['', Validators.required],
      description: [''],
    })
  }

  async onSubmit() {
    if (this.groupeForm.valid) {
      const formData = this.groupeForm.value;
      console.log('🧾 Données du formulaire :', formData);
      const group: GroupDTO = {
        nomGroupe: formData.nomGroupe,
        description: formData.description,
      };

      const result = await this.groupeService.createGroup(group);

      if (result.success) {
        console.log('✅ Groupe créé avec succès');
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
