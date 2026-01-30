import { ComponentFixture, TestBed } from '@angular/core/testing';
import {MaintenanceSheetDisplayComponent} from './maintenance-sheet-display';



describe('MaintenanceSheetDisplayComponent', () => {
  let component: MaintenanceSheetDisplayComponent;
  let fixture: ComponentFixture<MaintenanceSheetDisplayComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MaintenanceSheetDisplayComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MaintenanceSheetDisplayComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
