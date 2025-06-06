import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftIdeaFormComponent } from './gift-idea-form.component';

describe('GiftIdeaFormComponent', () => {
  let component: GiftIdeaFormComponent;
  let fixture: ComponentFixture<GiftIdeaFormComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftIdeaFormComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftIdeaFormComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
