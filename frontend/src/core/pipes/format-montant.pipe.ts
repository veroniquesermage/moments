import {Pipe, PipeTransform} from '@angular/core';

@Pipe({ name: 'formatMontant' })
export class FormatMontantPipe implements PipeTransform {
  transform(value: number | undefined): string {
    if(!value) return '0,00'; // Valeur par défaut si undefined ou null
    return new Intl.NumberFormat('fr-FR', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(value);
  }
}
