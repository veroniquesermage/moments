import {Injectable} from '@angular/core';
import {BehaviorSubject} from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ViewportService {
  private isPortraitSubject = new BehaviorSubject<boolean>(this.checkPortrait());

  isPortrait$ = this.isPortraitSubject.asObservable();

  constructor() {
    window.addEventListener('resize', this.update.bind(this));
  }

  private update() {
    this.isPortraitSubject.next(this.checkPortrait());
  }

  private checkPortrait(): boolean {
    return window.innerWidth < 768 && window.innerHeight > window.innerWidth;
  }
}
