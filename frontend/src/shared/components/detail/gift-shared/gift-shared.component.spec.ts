import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftSharedComponent } from './gift-shared.component';

describe('GiftSharedComponent', () => {
  let component: GiftSharedComponent;
  let fixture: ComponentFixture<GiftSharedComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftSharedComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftSharedComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
