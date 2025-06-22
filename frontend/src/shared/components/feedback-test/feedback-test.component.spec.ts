import { ComponentFixture, TestBed } from '@angular/core/testing';

import { FeedbackTestComponent } from './feedback-test.component';

describe('FeedbackTestComponent', () => {
  let component: FeedbackTestComponent;
  let fixture: ComponentFixture<FeedbackTestComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [FeedbackTestComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(FeedbackTestComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
