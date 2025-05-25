import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftActionsComponent } from './gift-actions.component';

describe('GiftActionsComponent', () => {
  let component: GiftActionsComponent;
  let fixture: ComponentFixture<GiftActionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftActionsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftActionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
