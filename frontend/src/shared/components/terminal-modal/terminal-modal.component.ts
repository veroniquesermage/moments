import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  Output,
  QueryList,
  ViewChildren
} from '@angular/core';
import { CommonModule } from '@angular/common';
import {TerminalModalAction} from 'src/core/models/terminal-modal-action.model';
import {CdkTrapFocus} from '@angular/cdk/a11y';

@Component({
  selector: 'app-terminal-modal',
  standalone: true,
  imports: [CommonModule, CdkTrapFocus],
  templateUrl: './terminal-modal.component.html',
  styleUrl: './terminal-modal.component.scss'
})
export class TerminalModalComponent implements AfterViewInit{
  @Input() message: string = "Êtes-vous sûr(e) ?";
  @Input() actions: TerminalModalAction[] = [];
  @Output() actionClicked = new EventEmitter<string>();

  @ViewChildren('focusBtn') boutons!: QueryList<ElementRef<HTMLButtonElement>>;

  ngAfterViewInit(): void {
    // Attend que l'affichage soit prêt, puis focus le premier bouton
    setTimeout(() => {
      const premierBouton = this.boutons.first;
      if (premierBouton) {
        premierBouton.nativeElement.focus();
      }
    });
  }
}
