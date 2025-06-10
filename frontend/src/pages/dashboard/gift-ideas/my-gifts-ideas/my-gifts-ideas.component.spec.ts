import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MyGiftsIdeasComponent } from './my-gifts-ideas.component';

describe('MyGiftsIdeasComponent', () => {
  let component: MyGiftsIdeasComponent;
  let fixture: ComponentFixture<MyGiftsIdeasComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MyGiftsIdeasComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MyGiftsIdeasComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
