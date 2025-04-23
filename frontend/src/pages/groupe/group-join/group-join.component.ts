import {Component} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormBuilder, FormGroup, ReactiveFormsModule, Validators} from '@angular/forms';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';

@Component({
  selector: 'app-group-join',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './group-join.component.html',
  styleUrl: './group-join.component.scss'
})
export class GroupJoinComponent {

  groupeForm: FormGroup;
  errorMessage: string | null = null;


  constructor(private fb: FormBuilder,
              private groupeService: GroupService,
              public router: Router) {
    this.groupeForm = this.fb.group({
      code: ['', Validators.required]
    })
  }

  async onSubmit() {
    if (this.groupeForm.valid) {
      let value = this.groupeForm.value;
      const result = await this.groupeService.joinGroup(value.code);

      if (result.success) {
        this.router.navigate(['groupe', 'dashboard']);
      } else {
        this.errorMessage = result.message!;
      }

    } else {
      console.warn('❌ Formulaire invalide');
      this.errorMessage = '❌ Formulaire invalide';
    }
  }
}
