import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftFormComponent } from './gift-form.component';

describe('GiftFormComponent', () => {
  let component: GiftFormComponent;
  let fixture: ComponentFixture<GiftFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
