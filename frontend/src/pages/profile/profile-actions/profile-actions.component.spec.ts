import { ComponentFixture, TestBed } from '@angular/core/testing';

import { ProfileActionsComponent } from './profile-actions.component';

describe('ProfileActionsComponent', () => {
  let component: ProfileActionsComponent;
  let fixture: ComponentFixture<ProfileActionsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ProfileActionsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ProfileActionsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
