import {ComponentFixture, TestBed} from '@angular/core/testing';

import {ManagedAccountsComponent} from './managed-accounts.component';

describe('ManagedAccountsComponent', () => {
  let component: ManagedAccountsComponent;
  let fixture: ComponentFixture<ManagedAccountsComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [ManagedAccountsComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(ManagedAccountsComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
