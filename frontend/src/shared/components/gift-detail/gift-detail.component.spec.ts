import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftDetailComponent } from './gift-detail.component';

describe('GiftDetailComponent', () => {
  let component: GiftDetailComponent;
  let fixture: ComponentFixture<GiftDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftDetailComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
