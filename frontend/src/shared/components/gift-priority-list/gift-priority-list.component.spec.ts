import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftPriorityListComponent } from './gift-priority-list.component';

describe('GiftPriorityListComponent', () => {
  let component: GiftPriorityListComponent;
  let fixture: ComponentFixture<GiftPriorityListComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftPriorityListComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftPriorityListComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
