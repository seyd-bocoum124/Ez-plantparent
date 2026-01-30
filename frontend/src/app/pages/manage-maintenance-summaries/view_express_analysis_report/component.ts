import {Component, signal} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {StationService} from '../../../services/station.service';
import {ReportSeriesService} from '../../../services/report-series.service';
import {parseArrayOrNull} from '../../../utils/utils';
import {ExpressLiveChartComponent} from '../../../components/express-live-chart/express-live-chart.component';
import {BreadcrumbService} from '../../../services/breadcrumb.service';



@Component({
  selector: 'app-view-express-analysis-report',
  standalone: true,
  templateUrl: './component.html',
  imports: [
    ExpressLiveChartComponent,
  ],
  styleUrls: ['./component.scss']
})
export class ViewExpressAnalysisReportComponent {
  expressAnalysisReport = signal<any>(undefined);

  constructor(
    private route: ActivatedRoute,
    private stationService: StationService,
    private seriesService: ReportSeriesService,
    private breadcrumbService: BreadcrumbService
  ) {}

  async ngOnInit() {
    const reportId = Number(this.route.snapshot.paramMap.get('reportId'));
    const plantId = Number(this.route.snapshot.paramMap.get('plantId'));

    this.breadcrumbService.setItems([
      { label: 'Accueil', routerLink: ['/accueil'],
        childs: [
          {label: 'Maintenance', routerLink: ['/maintenance-schedule']},
          {label: 'Plantes', routerLink: ['/my-plants']},
        ]
      },
      { label: 'Maintenance', routerLink: ['/maintenance-schedule'], queryParams: { plantId: plantId }},
      { label: 'Historique', routerLink: ['/my-plants', plantId, 'maintenance-summaries'] },
      { label: 'Analyse', routerLink: ['/my-plants', plantId, 'maintenance-summaries', 'express-analysis', reportId] }
    ]);

    this.stationService.getExpressAnalysisReportById(reportId).subscribe((data: any) => {
      this.expressAnalysisReport.set(data);

      const report = {
        soil_humidity_data: data.soil_humidity_data || [],
        air_humidity_data: data.air_humidity_data || [],
        temperature_data: data.temperature_data || [],
      };

      this.seriesService.setInitialSeries([
        { name: 'Soil humidity', data: parseArrayOrNull(report.soil_humidity_data) },
        { name: 'Air humidity', data: parseArrayOrNull(report.air_humidity_data) },
        { name: 'Temperature', data: parseArrayOrNull(report.temperature_data) }
      ]);

    });
  }
}

