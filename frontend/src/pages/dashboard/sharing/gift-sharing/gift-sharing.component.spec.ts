import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftSharingComponent } from './gift-sharing.component';

describe('GiftSharingComponent', () => {
  let component: GiftSharingComponent;
  let fixture: ComponentFixture<GiftSharingComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftSharingComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftSharingComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
