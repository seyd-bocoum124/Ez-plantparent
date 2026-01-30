// src/app/components/express-live-chart/express-live-chart.component.ts
import { Component, OnDestroy, OnInit, ViewChild } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ChartComponent, NgApexchartsModule } from 'ng-apexcharts';
import { Subscription } from 'rxjs';
import { ReportSeriesService, Series } from '../../services/report-series.service';

type ChartOptions = {
  series: Series[];
  chart: any;
  xaxis: any;
  stroke: any;
  markers: any;
  legend: any;
  dataLabels: any;
  grid: any;
  yaxis?: any;
  title?: any;
};

@Component({
  selector: 'app-express-live-chart',
  standalone: true,
  imports: [CommonModule, NgApexchartsModule],
  templateUrl: './express-live-chart.component.html',
  styleUrls: ['./express-live-chart.component.scss']
})
export class ExpressLiveChartComponent implements OnInit, OnDestroy {
  @ViewChild('chart') chart?: ChartComponent;

  chartSeries: Series[] = [];
  chartOptions!: ChartOptions;
  private sub?: Subscription;

  constructor(private seriesService: ReportSeriesService) {}

  ngOnInit(): void {
    this.chartOptions = {
      series: [],
      chart: {
        type: 'line',
        height: 360,
        animations: { enabled: false }, // pour updates fréquents
        toolbar: { show: true }
      },
      stroke: { curve: 'smooth', width: 2 },
      xaxis: { categories: [] as number[], title: { text: 'Measurement index' } },
      markers: { size: 3 },
      legend: { position: 'top' },
      dataLabels: { enabled: false },
      grid: { row: { colors: ['#f3f3f3', 'transparent'], opacity: 0.5 } },
      yaxis: [{ title: { text: 'Value' } }],
      title: { text: 'Express analysis (live)', align: 'left' }
    };

    this.sub = this.seriesService.series$.subscribe(series => {
      this.chartSeries = series;
      // met à jour les catégories x en fonction de la série la plus longue
      const maxLen = Math.max(...series.map(s => s.data.length), 0);
      this.chartOptions.xaxis.categories = Array.from({ length: maxLen }, (_, i) => i + 1);
      // update in-place via l'API du chart si disponible
      try {
        // Apex attend series au format [{ name, data }]
        this.chart?.updateSeries(series as any, true);
      } catch {
        // fallback pour forcer la détection Angular
        this.chartOptions = { ...this.chartOptions, series: series };
      }
    });
  }

  ngOnDestroy(): void {
    this.sub?.unsubscribe();
  }
}
