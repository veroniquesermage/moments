import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftDetailPageComponent } from './gift-detail-page.component';

describe('GiftDetailPageComponent', () => {
  let component: GiftDetailPageComponent;
  let fixture: ComponentFixture<GiftDetailPageComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftDetailPageComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftDetailPageComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
