import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftCreateComponent } from './gift-create.component';

describe('GiftCreateComponent', () => {
  let component: GiftCreateComponent;
  let fixture: ComponentFixture<GiftCreateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftCreateComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftCreateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
