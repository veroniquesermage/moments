import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GiftFollowUpDetailComponent } from './gift-follow-up-detail.component';

describe('GiftFollowUpDetailComponent', () => {
  let component: GiftFollowUpDetailComponent;
  let fixture: ComponentFixture<GiftFollowUpDetailComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GiftFollowUpDetailComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GiftFollowUpDetailComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
