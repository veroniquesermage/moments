import {ComponentFixture, TestBed} from '@angular/core/testing';

import {GiftTableComponent} from './gift-table.component';

describe('GiftTableComponent', () => {
  let component: GiftTableComponent;
  let fixture: ComponentFixture<GiftTableComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftTableComponent]
    })
      .compileComponents();

    fixture = TestBed.createComponent(GiftTableComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
