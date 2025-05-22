import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyGiftsFollowUpComponent } from './my-gifts-follow-up.component';

describe('MyGiftsFollowUpComponent', () => {
  let component: MyGiftsFollowUpComponent;
  let fixture: ComponentFixture<MyGiftsFollowUpComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyGiftsFollowUpComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MyGiftsFollowUpComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
