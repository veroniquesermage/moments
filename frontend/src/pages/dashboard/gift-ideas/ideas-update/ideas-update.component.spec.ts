import { ComponentFixture, TestBed } from '@angular/core/testing';

import { IdeasUpdateComponent } from './ideas-update.component';

describe('IdeasUpdateComponent', () => {
  let component: IdeasUpdateComponent;
  let fixture: ComponentFixture<IdeasUpdateComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [IdeasUpdateComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(IdeasUpdateComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
