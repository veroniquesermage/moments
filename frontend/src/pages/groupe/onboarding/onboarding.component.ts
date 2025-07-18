import {Component, OnInit} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {GroupContextService} from 'src/core/services/group-context.service';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {GroupResume} from 'src/core/models/group/group-resume.model';

@Component({
  selector: 'app-onboarding',
  standalone: true,
  imports: [CommonModule, FeedbackTestComponent],
  templateUrl: './onboarding.component.html',
  styleUrl: './onboarding.component.scss'
})
export class OnboardingComponent implements OnInit {

  errorMessage: string | null = null;
  composant: string = "OnboardingComponent";

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

  async choisirGroupe(groupe: GroupResume): Promise<void> {
    await this.groupContextService.setGroupContext(groupe.id);
    this.router.navigate(['/dashboard']);
  }

}
