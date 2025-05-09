import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TerminalConfirmModalComponent } from './terminal-confirm-modal.component';

describe('TerminalConfirmModalComponent', () => {
  let component: TerminalConfirmModalComponent;
  let fixture: ComponentFixture<TerminalConfirmModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TerminalConfirmModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TerminalConfirmModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
