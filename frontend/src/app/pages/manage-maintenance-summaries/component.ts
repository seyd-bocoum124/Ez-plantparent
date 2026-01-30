import { Component } from '@angular/core';
import {MaintenanceSheetService} from '../../services/maintenance-sheets.service';
import {ActivatedRoute, RouterLink} from '@angular/router';
import {DatePipe, TitleCasePipe} from '@angular/common';
import { MatTabsModule } from '@angular/material/tabs';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import {
  MatCell, MatCellDef,
  MatColumnDef,
  MatHeaderCell, MatHeaderCellDef,
  MatHeaderRow, MatHeaderRowDef,
  MatRow, MatRowDef,
  MatTable
} from '@angular/material/table';
import {MatButton} from '@angular/material/button';
import {BreadcrumbService} from '../../services/breadcrumb.service';



@Component({
  selector: 'app-maintenance-summaries-management',
  standalone: true,
  templateUrl: './component.html',
  imports: [
    DatePipe,
    TitleCasePipe,
    CommonModule,
    MatTabsModule,
    MatListModule,
    MatIconModule,
    MatHeaderCell,
    MatCell,
    MatHeaderRow,
    MatRow,
    MatTable,
    MatColumnDef,
    MatCellDef,
    MatHeaderCellDef,
    MatHeaderRowDef,
    MatRowDef,
    RouterLink,
    MatButton,
  ],
  styleUrls: ['./component.scss']
})
export class MaintenanceSummariesManagementComponent {
  constructor(
    private route: ActivatedRoute,
    private maintenanceSheetService: MaintenanceSheetService,
    private breadcrumbService: BreadcrumbService
  ) {}


  displayedColumns = [
    'type',
    'created_at',
    'soil_humidity_mean',
    'lumens_mean',
    'air_humidity_mean',
    'temperature_mean',
    'details'
  ];


  get summaries() {
    return this.maintenanceSheetService.summaries();
  }

  async ngOnInit() {
    const plantId = Number(this.route.snapshot.paramMap.get('plantId'));

    this.breadcrumbService.setItems([
      { label: 'Accueil', routerLink: ['/accueil'],
        childs: [
          {label: 'Maintenance', routerLink: ['/maintenance-schedule']},
          {label: 'Plantes', routerLink: ['/my-plants']},
        ]
      },
      { label: 'Maintenance', routerLink: ['/maintenance-schedule'], queryParams: { plantId: plantId }},
      { label: 'Historique', routerLink: ['/maintenance-schedule', plantId, 'maintenance-summaries'] },
    ]);


    await this.maintenanceSheetService.loadSummaries(plantId);
  }
}
