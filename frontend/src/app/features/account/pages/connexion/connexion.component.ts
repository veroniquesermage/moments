import {Component, OnInit} from '@angular/core';
import {AccountService} from '../../services/account.service';
import {Router} from '@angular/router';
import {ROUTES} from 'src/app/routes';

@Component({
  selector: 'app-connexion',
  templateUrl: './connexion.component.html',
  standalone: true
})
export class ConnexionComponent implements OnInit {
  status: string = 'loading';
  groupId?: number;
  groupes: any[] = [];

  constructor(private account: AccountService,
              private router: Router) {
  }

  ngOnInit(): void {
    console.log('[ConnexionComponent] Initialisé');

    this.account.getGroupStatus().subscribe({
      next: (res) => {
        switch (res.status) {
          case 'one_group':
            this.router.navigate([ROUTES.accueil]);
            break;

          case 'multiple_groups':
            this.status = res.status;
            this.groupes = res.groupes ?? [];
            break;

          case 'no_group':
            this.router.navigate([ROUTES.creationGroupe]);
            break;
        }
      },
      error: (err) => {
        console.error('[ConnexionComponent] Erreur reçue :', err);
        this.status = 'unauthorized';
      }
    });
  }

}
