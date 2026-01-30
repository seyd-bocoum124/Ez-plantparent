import { Component, Inject } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatIcon } from '@angular/material/icon';
import { MatMenuItem } from '@angular/material/menu';
import { MatBottomSheet, MAT_BOTTOM_SHEET_DATA } from '@angular/material/bottom-sheet';

@Component({
  selector: 'maintenance-actions-sheet',
  standalone: true,
  imports: [CommonModule, MatIcon, MatMenuItem],
  templateUrl: './component.html',
  styleUrls: ['./component.scss']
})
export class MaintenanceActionsSheet {
  constructor(
    @Inject(MAT_BOTTOM_SHEET_DATA) public data: { plantId: number },
    private bottomSheet: MatBottomSheet
  ) {}

  selectAction(action: string): void {
    const routes: any = {
      watering: ['/watering', this.data.plantId],
      analyze: ['/analyse/expresse', this.data.plantId],
      history: ['/my-plants', this.data.plantId, 'maintenance-summaries']
    };
    
    this.bottomSheet.dismiss({ route: routes[action] });
  }
}
