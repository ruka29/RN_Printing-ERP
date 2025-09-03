import { ComponentFixture, TestBed } from '@angular/core/testing';

import { PoEnterComponent } from './po-enter.component';

describe('PoEnterComponent', () => {
  let component: PoEnterComponent;
  let fixture: ComponentFixture<PoEnterComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [PoEnterComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(PoEnterComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
