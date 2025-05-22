import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftDeliverComponent } from './gift-deliver.component';

describe('GiftDeliverComponent', () => {
  let component: GiftDeliverComponent;
  let fixture: ComponentFixture<GiftDeliverComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftDeliverComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftDeliverComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
