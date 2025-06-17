import { Pipe, PipeTransform } from '@angular/core';
import {UserDisplay} from 'src/core/models/user-display.model';

@Pipe({
  name: 'displayName',
  standalone: true
})
export class DisplayNamePipe implements PipeTransform {

  transform(value: UserDisplay, complet: boolean = false): string {
    if (value.surnom) return value.surnom;
    return complet && value.nom ? `${value.prenom} ${value.nom}` : value.prenom || 'Utilisateur inconnu';
  }


}
