import {Component, inject, OnInit} from '@angular/core';
import {CommonModule} from '@angular/common';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';
import {GroupService} from 'src/core/services/group.service';
import {ActivatedRoute, Router} from '@angular/router';
import {ErrorService} from 'src/core/services/error.service';
import {TerminalModalComponent} from 'src/shared/components/terminal-modal/terminal-modal.component';
import {FeedbackTestComponent} from 'src/shared/components/feedback-test/feedback-test.component';
import {AuthService} from 'src/security/service/auth.service';

@Component({
  selector: 'app-group-join',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, TerminalModalComponent, FeedbackTestComponent, FormsModule],
  templateUrl: './group-join.component.html',
  styleUrl: './group-join.component.scss'
})
export class GroupJoinComponent implements OnInit{

  composant: string = "GroupJoinComponent";
  codeInvitation: string = '';
  private route = inject(ActivatedRoute);

  constructor(private groupeService: GroupService,
              public router: Router,
              public errorService: ErrorService,
              private authService: AuthService) {
  }

  ngOnInit() {
    this.route.queryParams.subscribe(params => {
      this.codeInvitation = params['inviteCode'] ?? '';
      if (!this.authService.isLoggedIn()) {
        localStorage.setItem('app_kdo.codeInvit', this.codeInvitation);
        this.authService.login();
      } else {
        localStorage.removeItem('app_kdo.codeInvit');
      }
    });
  }

  async rejoindre() {
      const result = await this.groupeService.joinGroup(this.codeInvitation);
      if (result.success) {
        await this.router.navigate(['/dashboard']);
      } else {
        this.errorService.showError(result.message);
      }
  }
}
