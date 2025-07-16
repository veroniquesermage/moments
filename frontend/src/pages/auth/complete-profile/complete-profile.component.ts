import {Component, inject, OnInit} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {AuthService} from 'src/security/service/auth.service';
import {CommonModule} from '@angular/common';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {ErrorService} from 'src/core/services/error.service';
import {ActivatedRoute} from '@angular/router';
import {IncompleteUser} from 'src/security/model/incomplete_user.model';

@Component({
  selector: 'app-complete-profile',
  standalone: true,
  imports: [
    FormsModule,
    CommonModule,
    FeedbackTestComponent,
    TerminalModalComponent
  ],
  templateUrl: './complete-profile.component.html',
  styleUrl: './complete-profile.component.scss'
})
export class CompleteProfileComponent implements OnInit{

  composant: string = "CompleteProfileComponent";
  givenName: string | undefined ='';
  familyName: string | undefined ='';
  user: IncompleteUser | null = null;
  context: 'google' | 'credentials' | 'compte-mandataire' = 'google';
  token: string | null = null;
  private route = inject(ActivatedRoute);

  constructor(
    private authService: AuthService,
    public errorService: ErrorService
  ) {}

  ngOnInit(): void {
    this.user = this.authService.incompleteUser();
    this.givenName = this.user ? this.user.prenom : '';
    this.familyName = this.user ? this.user.nom : '';

    const contexteBrut = this.route.snapshot.queryParamMap.get('context');
    const contextValide = ['google', 'credentials', 'compte-mandataire'].includes(contexteBrut ?? '');
    this.context = (contextValide ? contexteBrut : 'google') as 'google' | 'credentials' | 'compte-mandataire';

    console.log(this.context);
    this.token = this.route.snapshot.queryParamMap.get('token');
    }

  submitName() {
    if (!this.givenName!.trim()) {
      this.errorService.showError("Le prénom est obligatoire.");
      return;
    }

    this.authService.completeProfile(this.givenName!.trim(), this.familyName?.trim())
      .catch(() => {
        this.errorService.showError("Une erreur est survenue lors de la mise à jour du profil.");
      });
  }

  async registerWithCredentials() {
    if (!this.givenName!.trim()) {
      this.errorService.showError("Le prénom est obligatoire.");
      return;
    }
    await this.authService.registerWithCredentials(this.givenName!.trim(), this.familyName?.trim(), this.token)
  }
}
