import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftHeaderComponent } from './gift-header.component';

describe('GiftHeaderComponent', () => {
  let component: GiftHeaderComponent;
  let fixture: ComponentFixture<GiftHeaderComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftHeaderComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftHeaderComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
