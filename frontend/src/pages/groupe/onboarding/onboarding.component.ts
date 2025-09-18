import {Component, OnInit} from '@angular/core';
import {GroupService} from 'src/core/services/group.service';
import {Router} from '@angular/router';
import {CommonModule} from '@angular/common';
import {GroupContextService} from 'src/core/services/group-context.service';
import {GroupResume} from 'src/core/models/group/group-resume.model';

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
    // Check if there's a stored invitation token from email link
    const storedToken = localStorage.getItem('app_kdo.inviteToken');
    if (storedToken) {
      // Redirect to the join page with the token
      void this.router.navigate(['/groupe/onboarding/rejoindre'], {
        queryParams: { inviteToken: storedToken }
      });
      return;
    }

    this.groupService.loadGroupesIfEmpty().then(result => {
      if ('success' in result && result.success) {
        console.log('📦 Groupes récupérés :', result.data);
        // Si tu veux faire des actions ici (auto-select, etc.), c'est l'endroit
      } else {
        this.errorMessage = result.message ?? "Erreur inconnue";
      }
    });
  }

  async choisirGroupe(groupe: GroupResume): Promise<void> {
    await this.groupContextService.setGroupContext(groupe.id);
    void this.router.navigate(['/dashboard']);
  }

}
