import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GroupRolesComponent } from './group-roles.component';

describe('GroupRolesComponent', () => {
  let component: GroupRolesComponent;
  let fixture: ComponentFixture<GroupRolesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GroupRolesComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GroupRolesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
