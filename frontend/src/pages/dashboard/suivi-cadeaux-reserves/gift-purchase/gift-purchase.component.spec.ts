import {ComponentFixture, TestBed} from '@angular/core/testing';

import {GiftPurchaseComponent} from './gift-purchase.component';

describe('GiftPurchaseComponent', () => {
  let component: GiftPurchaseComponent;
  let fixture: ComponentFixture<GiftPurchaseComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftPurchaseComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftPurchaseComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
