import {Component, signal} from '@angular/core';
import {ActivatedRoute} from '@angular/router';
import {StationService} from '../../../services/station.service';
import {ReportSeriesService} from '../../../services/report-series.service';
import {parseArrayOrNull} from '../../../utils/utils';
import {ExpressLiveChartComponent} from '../../../components/express-live-chart/express-live-chart.component';
import {BreadcrumbService} from '../../../services/breadcrumb.service';



@Component({
  selector: 'app-view-watering-report',
  standalone: true,
  templateUrl: './component.html',
  imports: [
    ExpressLiveChartComponent,
  ],
  styleUrls: ['./component.scss']
})
export class ViewWateringReportComponent {
  wateringReport = signal<any>(undefined);


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
      { label: 'Arrosage', routerLink: ['/my-plants', plantId, 'maintenance-summaries', 'watering', reportId] }
    ]);


    this.stationService.getWateringReportById(reportId).subscribe((data: any) => {
      this.wateringReport.set(data);
      const report = {
        soil_humidity_data: data.soil_humidity_data || [],
        pump_data: data.pump_data || [],
      };

      let humidityData = parseArrayOrNull(report.soil_humidity_data);

      this.seriesService.setInitialSeries([
        { name: 'Soil humidity', data: humidityData },
        { name: 'Pump', data: parseArrayOrNull(report.pump_data) },
        { name: 'Target Humidity', data: humidityData.map(i => data.target_humidity || null) },
      ]);

    });
  }
}

