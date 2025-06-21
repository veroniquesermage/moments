import { Pipe, PipeTransform } from '@angular/core';
import {UserDisplay} from 'src/core/models/user-display.model';

@Pipe({
  name: 'displayName',
  standalone: true
})
export class DisplayNamePipe implements PipeTransform {

  transform(user: UserDisplay | null | undefined, complet: boolean = false): string {
    if (!user) return '—'; // ou autre fallback si tu préfères
    if (user.surnom) return user.surnom;
    return complet && user.nom ? `${user.prenom} ${user.nom}` : user.prenom || 'Utilisateur inconnu';
  }


}
