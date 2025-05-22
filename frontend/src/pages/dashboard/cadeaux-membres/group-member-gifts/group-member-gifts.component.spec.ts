import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GroupMemberGiftsComponent } from './group-member-gifts.component';

describe('GroupMemberGiftsComponent', () => {
  let component: GroupMemberGiftsComponent;
  let fixture: ComponentFixture<GroupMemberGiftsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GroupMemberGiftsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GroupMemberGiftsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
