import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class UserInteractionService {
  private isTabbing = new BehaviorSubject<boolean>(false);
  public readonly isTabbing$ = this.isTabbing.asObservable();

  constructor() {
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Tab') this.isTabbing.next(true);
    });

    document.addEventListener('mousedown', () => {
      this.isTabbing.next(false);
    });
  }
}
