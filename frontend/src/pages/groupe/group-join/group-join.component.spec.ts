import {ComponentFixture, TestBed} from '@angular/core/testing';

import {GroupJoinComponent} from './group-join.component';

describe('GroupJoinComponent', () => {
  let component: GroupJoinComponent;
  let fixture: ComponentFixture<GroupJoinComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GroupJoinComponent]
    })
      .compileComponents();

    fixture = TestBed.createComponent(GroupJoinComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
