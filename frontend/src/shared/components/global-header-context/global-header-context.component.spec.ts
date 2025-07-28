import {ComponentFixture, TestBed} from '@angular/core/testing';

import {GlobalHeaderContextComponent} from './global-header-context.component';

describe('GlobalHeaderContextComponent', () => {
  let component: GlobalHeaderContextComponent;
  let fixture: ComponentFixture<GlobalHeaderContextComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [GlobalHeaderContextComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(GlobalHeaderContextComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
