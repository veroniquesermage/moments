import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TerminalModalComponent } from './terminal-modal.component';

describe('TerminalModalComponent', () => {
  let component: TerminalModalComponent;
  let fixture: ComponentFixture<TerminalModalComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TerminalModalComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TerminalModalComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
