import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MaintenanceSheetsManagement } from './maintenance-sheets-management';

describe('MaintenanceSheetsManagement', () => {
  let component: MaintenanceSheetsManagement;
  let fixture: ComponentFixture<MaintenanceSheetsManagement>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MaintenanceSheetsManagement]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MaintenanceSheetsManagement);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
