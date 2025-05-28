import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftStatutComponent } from './gift-statut.component';

describe('GiftStatutComponent', () => {
  let component: GiftStatutComponent;
  let fixture: ComponentFixture<GiftStatutComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftStatutComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftStatutComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
