// src/app/features/app/pages/app-home.component.ts
import {Component, OnInit} from '@angular/core';
import {Router} from '@angular/router';
import {AccountService} from '../../../account/services/account.service';
import {ROUTES} from 'src/app/routes';

@Component({
  selector: 'app-home',
  standalone: true,
  template: '<p>Chargement de vos informations...</p>'
})
export class AppHomeComponent implements OnInit {
  constructor(private account: AccountService, private router: Router) {
  }

  ngOnInit(): void {
    this.account.getGroupStatus().subscribe({
      next: (res) => {
        console.log('Résultat de /groups/choose :', res);

        switch (res.status) {
          case 'one_group':
            console.log('Redirection vers groupe unique :', ROUTES.groupes, res.groupId);
            this.router.navigate([ROUTES.groupes, res.groupId]);
            break;

          case 'multiple_groups':
            console.log('Redirection vers le choix du groupe');
            this.router.navigate([ROUTES.connexion, 'choose']);
            break;

          case 'no_group':
            console.log('Redirection vers création de groupe');
            this.router.navigate([ROUTES.creationGroupe]);
            break;
        }
      },
      error: () => {
        console.log('Erreur dans /groups/choose → redirection vers la connexion');
        this.router.navigate([ROUTES.connexion]);
      }
    });
  }
}
