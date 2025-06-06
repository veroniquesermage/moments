import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftIdeaComponent } from './gift-idea.component';

describe('GiftIdeaComponent', () => {
  let component: GiftIdeaComponent;
  let fixture: ComponentFixture<GiftIdeaComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftIdeaComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftIdeaComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
