import { Routes } from '@angular/router';
import {LandingComponent} from './pages/landing/landing';
import {MaintenanceSheetsManagement} from './pages/manage-plants/maintenance-sheets-management';
import {
  CreateMaintenanceSheet
} from './pages/manage-plants/create-plant-by-name/create-maintenance-sheet';
import {WateringPlantComponent} from './pages/watering/component';
import {
  CreateMaintenanceSheetByPictureComponent
} from './pages/manage-plants/create-plant-by-picture/component';
import {MaintenanceSummariesManagementComponent} from './pages/manage-maintenance-summaries/component';
import {ViewWateringReportComponent} from './pages/manage-maintenance-summaries/view_watering_report/component';
import {
  ViewExpressAnalysisReportComponent
} from './pages/manage-maintenance-summaries/view_express_analysis_report/component';
import {ExpressAnalysisComponent} from './pages/express-analysis/component';
import {PairStationComponent} from './pages/manage-station/component';
import {canActivateAuthGuard, canMatchAuthGuard} from './services/auth/auth.guard';
import {ViewDailyScheduleComponent} from './pages/manage-schedules/view-daily-schedule/component';
import {AccueilComponent} from './pages/accueil/component';


export const routes: Routes = [
  {
    path: 'stations',
    component: PairStationComponent,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'maintenance-schedule',
    component: ViewDailyScheduleComponent,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'analyse/expresse/:plantId',
    component: ExpressAnalysisComponent,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'accueil',
    component: AccueilComponent,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'watering/:plantId',
    component: WateringPlantComponent,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: '',
    component: LandingComponent
  },
  {
    path: 'my-plants',
    component: MaintenanceSheetsManagement,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'my-plants/print-qr',
    loadComponent: () => import('./pages/manage-plants/print-qr-codes/print-qr-codes.component').then(m => m.PrintQrCodesComponent),
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'my-plants/create',
    component: CreateMaintenanceSheet,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'my-plants/:plantId/maintenance-summaries',
    component: MaintenanceSummariesManagementComponent,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'my-plants/:plantId/maintenance-summaries/watering/:reportId',
    component: ViewWateringReportComponent,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'my-plants/:plantId/maintenance-summaries/express-analysis/:reportId',
    component: ViewExpressAnalysisReportComponent,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  },
  {
    path: 'my-plants/create/from-picture',
    component: CreateMaintenanceSheetByPictureComponent,
    canMatch: [canMatchAuthGuard],
    canActivate: [canActivateAuthGuard]
  }
];

