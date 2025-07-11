import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GroupInviteComponent } from './group-invite.component';

describe('GroupInviteComponent', () => {
  let component: GroupInviteComponent;
  let fixture: ComponentFixture<GroupInviteComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GroupInviteComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GroupInviteComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
