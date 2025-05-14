import { ComponentFixture, TestBed } from '@angular/core/testing';

import { TakeGiftComponent } from './take-gift.component';

describe('TakeGiftComponent', () => {
  let component: TakeGiftComponent;
  let fixture: ComponentFixture<TakeGiftComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TakeGiftComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(TakeGiftComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
