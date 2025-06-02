import {Component, OnInit} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {GroupeResume} from 'src/core/models/group-resume.model';
import {GroupContextService} from 'src/core/services/group-context.service';

@Component({
  selector: 'app-onboarding',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './onboarding.component.html',
  styleUrl: './onboarding.component.scss'
})
export class OnboardingComponent implements OnInit {

  errorMessage: string | null = null;

  constructor(
    public groupService: GroupService,
    public router: Router,
    public groupContextService: GroupContextService
  ) {
  }

  ngOnInit(): void {
    this.groupService.loadGroupesIfEmpty().then(result => {
      if ('success' in result && result.success) {
        console.log('📦 Groupes récupérés :', result.data);
        // Si tu veux faire des actions ici (auto-select, etc.), c’est l’endroit
      } else {
        this.errorMessage = result.message ?? "Erreur inconnue";
      }
    });
  }

  choisirGroupe(groupe: GroupeResume): void {
    this.groupContextService.setGroupContext(groupe.id);
        this.router.navigate(['/dashboard']);
  }

}
