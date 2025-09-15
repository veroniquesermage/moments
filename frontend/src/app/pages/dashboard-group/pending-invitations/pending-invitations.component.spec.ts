import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PendingInvitationsComponent } from './pending-invitations.component';

describe('PendingInvitationsComponent', () => {
  let component: PendingInvitationsComponent;
  let fixture: ComponentFixture<PendingInvitationsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PendingInvitationsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PendingInvitationsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
