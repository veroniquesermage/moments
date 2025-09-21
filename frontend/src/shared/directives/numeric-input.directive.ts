import { Directive, ElementRef, HostListener } from '@angular/core';

@Directive({
  selector: '[appNumericInput]',
  standalone: true
})
export class NumericInputDirective {

  constructor(private el: ElementRef) {}

  @HostListener('keydown', ['$event'])
  onKeyDown(event: KeyboardEvent): void {
    const allowedKeys = [
      'Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'Home', 'End',
      'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown'
    ];

    // Autorise les touches de contrôle
    if (allowedKeys.includes(event.key) ||
        event.ctrlKey || event.metaKey || event.altKey) {
      return;
    }

    const input = this.el.nativeElement as HTMLInputElement;
    const currentValue = input.value;
    const selectionStart = input.selectionStart || 0;
    const selectionEnd = input.selectionEnd || 0;

    // Autorise les chiffres
    if (/^[0-9]$/.test(event.key)) {
      return;
    }

    // Autorise le point décimal (.) et la virgule (,) - mais seulement un seul
    if ((event.key === '.' || event.key === ',') &&
        !currentValue.includes('.') && !currentValue.includes(',')) {
      return;
    }

    // Bloque tout le reste
    event.preventDefault();
  }

  @HostListener('input', ['$event'])
  onInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    let value = input.value;

    // Remplace la virgule par un point
    value = value.replace(',', '.');

    // Supprime tous les caractères non valides (garde seulement chiffres et un point)
    value = value.replace(/[^0-9.]/g, '');

    // Limite à un seul point décimal
    const parts = value.split('.');
    if (parts.length > 2) {
      value = parts[0] + '.' + parts.slice(1).join('');
    }

    // Met à jour la valeur si elle a changé
    if (input.value !== value) {
      input.value = value;
      // Déclenche l'événement input pour que Angular détecte le changement
      input.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }

  @HostListener('paste', ['$event'])
  onPaste(event: ClipboardEvent): void {
    event.preventDefault();

    const pastedText = event.clipboardData?.getData('text') || '';
    const input = this.el.nativeElement as HTMLInputElement;

    // Nettoie le texte collé
    let cleanedText = pastedText.replace(',', '.');
    cleanedText = cleanedText.replace(/[^0-9.]/g, '');

    // Limite à un seul point décimal
    const parts = cleanedText.split('.');
    if (parts.length > 2) {
      cleanedText = parts[0] + '.' + parts.slice(1).join('');
    }

    // Insère le texte nettoyé à la position du curseur
    const selectionStart = input.selectionStart || 0;
    const selectionEnd = input.selectionEnd || 0;
    const currentValue = input.value;

    const newValue = currentValue.substring(0, selectionStart) +
                     cleanedText +
                     currentValue.substring(selectionEnd);

    input.value = newValue;
    input.dispatchEvent(new Event('input', { bubbles: true }));

    // Repositionne le curseur
    const newCursorPosition = selectionStart + cleanedText.length;
    input.setSelectionRange(newCursorPosition, newCursorPosition);
  }
}