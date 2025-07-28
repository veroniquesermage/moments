import { Injectable, signal } from '@angular/core';

export type ToastType = 'success' | 'error' | 'info' | 'warning';
export interface ToastOptions {
  message: string;
  type?: ToastType;
  duration?: number;
}

interface Toast extends ToastOptions {
  id: number;
  type: ToastType;
  duration: number;
}

@Injectable({ providedIn: 'root' })
export class ToastrService {
  private toasts = signal<Toast[]>([]);

  show(options: ToastOptions) {
    const toast: Toast = {
      id: Date.now() + Math.random(),
      message: options.message,
      type: options.type ?? 'info',
      duration: options.duration ?? 3000,
    };
    this.toasts.update(ts => [...ts, toast]);
    setTimeout(() => this.remove(toast.id), toast.duration);
  }

  remove(id: number) {
    this.toasts.update(ts => ts.filter(t => t.id !== id));
  }

  toastsSignal() {
    return this.toasts.asReadonly();
  }
}
