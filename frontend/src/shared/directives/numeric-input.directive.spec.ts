import { Component, DebugElement } from '@angular/core';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { By } from '@angular/platform-browser';
import { NumericInputDirective } from './numeric-input.directive';

@Component({
  template: `<input appNumericInput [(ngModel)]="value" />`,
  standalone: true,
  imports: [NumericInputDirective]
})
class TestComponent {
  value = '';
}

describe('NumericInputDirective', () => {
  let component: TestComponent;
  let fixture: ComponentFixture<TestComponent>;
  let inputEl: DebugElement;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TestComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(TestComponent);
    component = fixture.componentInstance;
    inputEl = fixture.debugElement.query(By.css('input'));
  });

  it('should allow numeric input', () => {
    const event = new KeyboardEvent('keydown', { key: '5' });
    spyOn(event, 'preventDefault');

    inputEl.nativeElement.dispatchEvent(event);

    expect(event.preventDefault).not.toHaveBeenCalled();
  });

  it('should allow decimal point', () => {
    component.value = '123';
    fixture.detectChanges();

    const event = new KeyboardEvent('keydown', { key: '.' });
    spyOn(event, 'preventDefault');

    inputEl.nativeElement.dispatchEvent(event);

    expect(event.preventDefault).not.toHaveBeenCalled();
  });

  it('should allow comma and convert to dot', () => {
    component.value = '123';
    fixture.detectChanges();

    const event = new KeyboardEvent('keydown', { key: ',' });
    spyOn(event, 'preventDefault');

    inputEl.nativeElement.dispatchEvent(event);

    expect(event.preventDefault).not.toHaveBeenCalled();
  });

  it('should prevent multiple decimal points', () => {
    component.value = '123.45';
    fixture.detectChanges();

    const event = new KeyboardEvent('keydown', { key: '.' });
    spyOn(event, 'preventDefault');

    inputEl.nativeElement.dispatchEvent(event);

    expect(event.preventDefault).toHaveBeenCalled();
  });

  it('should prevent letters', () => {
    const event = new KeyboardEvent('keydown', { key: 'a' });
    spyOn(event, 'preventDefault');

    inputEl.nativeElement.dispatchEvent(event);

    expect(event.preventDefault).toHaveBeenCalled();
  });

  it('should prevent special characters', () => {
    const event = new KeyboardEvent('keydown', { key: '@' });
    spyOn(event, 'preventDefault');

    inputEl.nativeElement.dispatchEvent(event);

    expect(event.preventDefault).toHaveBeenCalled();
  });

  it('should allow control keys', () => {
    const controlKeys = ['Backspace', 'Delete', 'Tab', 'Enter', 'ArrowLeft', 'ArrowRight'];

    controlKeys.forEach(key => {
      const event = new KeyboardEvent('keydown', { key });
      spyOn(event, 'preventDefault');

      inputEl.nativeElement.dispatchEvent(event);

      expect(event.preventDefault).not.toHaveBeenCalled();
    });
  });
});