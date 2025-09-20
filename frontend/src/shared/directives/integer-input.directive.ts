import { Directive, ElementRef, HostListener } from '@angular/core';

@Directive({
  selector: '[appIntegerInput]',
  standalone: true
})
export class IntegerInputDirective {

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

    // Autorise seulement les chiffres pour les entiers
    if (/^[0-9]$/.test(event.key)) {
      return;
    }

    // Bloque tout le reste (y compris . et ,)
    event.preventDefault();
  }

  @HostListener('input', ['$event'])
  onInput(event: Event): void {
    const input = event.target as HTMLInputElement;
    let value = input.value;

    // Supprime tous les caractères non-chiffres
    value = value.replace(/[^0-9]/g, '');

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

    // Nettoie le texte collé - garde seulement les chiffres
    const cleanedText = pastedText.replace(/[^0-9]/g, '');

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