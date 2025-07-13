import {Component, OnInit} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {User} from 'src/security/model/user.model';
import {AuthService} from 'src/security/service/auth.service';
import {NgIf} from '@angular/common';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {ErrorService} from 'src/core/services/error.service';

@Component({
  selector: 'app-complete-profile',
  standalone: true,
  imports: [
    FormsModule,
    NgIf,
    FeedbackTestComponent,
    TerminalModalComponent
  ],
  templateUrl: './complete-profile.component.html',
  styleUrl: './complete-profile.component.scss'
})
export class CompleteProfileComponent implements OnInit{

  composant: string = "CompleteProfileComponent";
  givenName: string ='';
  familyName: string ='';
  user: User | null = null;

  constructor(
    private authService: AuthService,
    public errorService: ErrorService
  ) { }


  ngOnInit(): void {
        this.user = this.authService.profile();
        this.givenName = this.user ? this.user.prenom : '';
        this.familyName = this.user ? this.user.nom : '';
    }

  submitName() {
    if (!this.givenName.trim() || !this.familyName.trim()) {
      this.errorService.showError("Le prénom et le nom sont obligatoires.");
      return;
    }

    this.authService.completeProfile(this.givenName.trim(), this.familyName.trim())
      .catch(() => {
        this.errorService.showError("Une erreur est survenue lors de la mise à jour du profil.");
      });
  }

}
