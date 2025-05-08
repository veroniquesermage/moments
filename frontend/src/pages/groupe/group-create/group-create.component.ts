import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {GroupService} from 'src/core/services/group.service';
import {GroupeDTO} from 'src/core/models/groupe-dto.model';
import {Router} from '@angular/router';

@Component({
  selector: 'app-group-create',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './group-create.component.html',
  styleUrl: './group-create.component.scss'
})
export class GroupCreateComponent {

  groupeForm: FormGroup;
  errorMessage: string | null = null;

  constructor(private fb: FormBuilder,
              private groupeService: GroupService,
              public router: Router) {
    this.groupeForm = this.fb.group({
      nomGroupe: ['', Validators.required],
      description: [''],
    })
  }

  async onSubmit() {
    if (this.groupeForm.valid) {
      const formData = this.groupeForm.value;
      console.log('🧾 Données du formulaire :', formData);
      const group: GroupeDTO = {
        nomGroupe: formData.nomGroupe,
        description: formData.description,
      };

      const result = await this.groupeService.createGroup(group);

      if (result.success) {
        console.log('✅ Groupe créé avec succès');
        this.router.navigate(['/dashboard']);
      } else {
        this.errorMessage = result.message!;
      }

    } else {
      console.warn('❌ Formulaire invalide');
      this.errorMessage = '❌ Formulaire invalide';
    }
  }
}
