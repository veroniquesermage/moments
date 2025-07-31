import {ComponentFixture, TestBed} from '@angular/core/testing';

import {GiftPurchaseInfoComponent} from './gift-purchase-info.component';

describe('GiftPurchaseInfoComponent', () => {
  let component: GiftPurchaseInfoComponent;
  let fixture: ComponentFixture<GiftPurchaseInfoComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftPurchaseInfoComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftPurchaseInfoComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
