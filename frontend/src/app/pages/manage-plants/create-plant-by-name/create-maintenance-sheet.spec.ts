import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreateMaintenanceSheet } from './create-maintenance-sheet';

describe('CreateMaintenanceSheet', () => {
  let component: CreateMaintenanceSheet;
  let fixture: ComponentFixture<CreateMaintenanceSheet>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreateMaintenanceSheet]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreateMaintenanceSheet);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
