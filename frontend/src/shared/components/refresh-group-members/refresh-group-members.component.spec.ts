import { ComponentFixture, TestBed } from '@angular/core/testing';

import { RefreshGroupMembersComponent } from './refresh-group-members.component';

describe('RefreshGroupMembersComponent', () => {
  let component: RefreshGroupMembersComponent;
  let fixture: ComponentFixture<RefreshGroupMembersComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [RefreshGroupMembersComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(RefreshGroupMembersComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
