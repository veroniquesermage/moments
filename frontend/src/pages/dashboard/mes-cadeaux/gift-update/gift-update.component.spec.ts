import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftUpdateComponent } from './gift-update.component';

describe('GiftUpdateComponent', () => {
  let component: GiftUpdateComponent;
  let fixture: ComponentFixture<GiftUpdateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftUpdateComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftUpdateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
