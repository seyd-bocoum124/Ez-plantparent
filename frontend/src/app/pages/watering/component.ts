import {
  Component,
  OnDestroy,
  OnInit,
  ChangeDetectorRef,
  ChangeDetectionStrategy,
  signal,
  ViewChild,
  effect
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { Subscription } from 'rxjs';
import {MatButton} from '@angular/material/button';
import {MatChip, MatChipListbox} from '@angular/material/chips';
import {ActivatedRoute, RouterLink} from '@angular/router';
import * as _ from 'lodash';
import {MatStep, MatStepLabel, MatStepper, MatStepperNext} from '@angular/material/stepper';
import {StepperSelectionEvent} from '@angular/cdk/stepper';
import {MatProgressBar} from '@angular/material/progress-bar';
import {WebsocketService} from '../../services/websocket.service';
import {StationService} from '../../services/station.service';
import {ReportSeriesService} from '../../services/report-series.service';
import {ExpressLiveChartComponent} from '../../components/express-live-chart/express-live-chart.component';
import {BreadcrumbService} from '../../services/breadcrumb.service';

enum StepIndex {
  TEST_SENSORS = 0,
  EXPRESS_ANALYSIS = 1,
  PRESENT_RESULTS = 2,
}


@Component({
  selector: 'watering-plant',
  standalone: true,
  imports: [CommonModule, MatButton, MatChipListbox, MatChip, MatStepper, MatStep, MatStepLabel, MatStepperNext, MatProgressBar, RouterLink, ExpressLiveChartComponent],
  templateUrl: './component.html',
  styleUrls: ['./component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})

export class WateringPlantComponent implements OnInit, OnDestroy {
  private sub?: Subscription;
  data: any = null;
  message: any;
  isTestingSensor: boolean = false;
  isExpressAnalysis: boolean = false;
  numberOfDataMessages:number = 0;
  reportId:number | null = null;
  wateringReport = signal<any>(undefined);
  @ViewChild('stepper') stepper!: MatStepper;

  constructor(
    private wsService: WebsocketService,
    private stationService: StationService,
    private seriesService: ReportSeriesService,
    private cdr: ChangeDetectorRef,
    private route: ActivatedRoute,
    private breadcrumbService: BreadcrumbService
  ) {
    // Effect qui observe le changement de station et connecte le WebSocket
    effect(() => {
      const stationId = this.activeStationMacAddress();
      if (stationId) {
        console.log('[Watering] Station changed to:', stationId);
        this.wsService.setStationId(stationId);
        this.connectWebSocket();
      }
    });
  }

  get activeStationMacAddress() {
    return this.stationService.activeStationMacAddress;
  }

  readonly ANALYSIS_SUCCESS_MESSAGE_DURATION = 4000;
  readonly TEST_SENSORS_DURATION = 60;
  readonly EXPRESS_ANALYSIS_DURATION = 15;
  plantId:  number | null = null;
  reportDeleted: boolean = false;


  ngOnInit(): void {
    const rawId = this.route.snapshot.paramMap.get('plantId');
    this.plantId = rawId !== null ? Number(rawId) : null;
    console.debug('[Watering] ngOnInit - WebSocket will connect via effect when stationId is available');

    this.breadcrumbService.setItems([
      { label: 'Accueil', routerLink: ['/accueil'],
        childs: [
          {label: 'Maintenance', routerLink: ['/maintenance-schedule']},
          {label: 'Plantes', routerLink: ['/my-plants']},
        ]
      },
      { label: 'Maintenance', routerLink: ['/maintenance-schedule'], queryParams: { plantId: this.plantId }},
      { label: 'Arroser' },
    ]);
  }

  ngAfterViewInit(): void {
    // Démarre le test des sensors dès que la vue est prête
    setTimeout(() => {
      this.sensorTest('start');
    }, 0);
  }

  private connectWebSocket(): void {
    // Nettoyer l'ancienne subscription si elle existe
    this.sub?.unsubscribe();

    this.sub = this.wsService.connect().subscribe({
      next: (msg) => {
        console.debug('[StationLive] recv', msg);
        this.pushMessage(msg);
        if(_.get(msg, "type") === "data") {
          this.numberOfDataMessages++;
          this.cdr.markForCheck();
          const data = _.get(msg, "data");
          this.seriesService.addPoints(
            _.get(data, "humidity"),
            null,
            null,
            _.get(data, "pump"),
            _.get(data, "target_humidity"),
          )
        } else if(JSON.stringify(_.pick(msg, ["type", "activity", "action"])) === JSON.stringify({'type': 'command', 'activity': 'send_data', 'action': 'ended'})) {
          console.log("Send all data ended!")
          this.isTestingSensor = false;
          this.cdr.markForCheck();
        } else if(JSON.stringify(_.pick(msg, ["type", "action", "activity"])) === JSON.stringify({"type":"command","action":"present_report", "activity": "watering"})) {
          const report_id = _.get(msg, "data.report_id");

          this.stationService.getWateringReportById(report_id).subscribe((data: any) => {
            this.wateringReport.set(data);
            const report = {
              soil_humidity_data: _.get(data, "soil_humidity_data", []),
              pump_data: _.get(data, "pump_data", []),
            };

            this.reportId = report_id;
            this.cdr.markForCheck();
            setTimeout(()=>  {
              this.goNextStep();
            }, this.ANALYSIS_SUCCESS_MESSAGE_DURATION);


            function parseArrayOrNull(s: string | null | undefined): (number | null)[] {
              if (!s) return [];
              try {
                const a = JSON.parse(s);
                if (!Array.isArray(a)) return [];
                return a.map((v: unknown) => (v === null ? null : Number.isFinite(v as number) ? (v as number) : null));
              } catch {
                return [];
              }
            }

            let humidityData = parseArrayOrNull(report.soil_humidity_data);

            this.seriesService.setInitialSeries([
              { name: 'Soil humidity', data: humidityData },
              { name: 'Pump', data: parseArrayOrNull(report.pump_data) },
              { name: 'Target Humidity', data: humidityData.map(i => data.target_humidity || null) },
            ]);

          });
        }
      },
      error: (err) => console.debug('[StationLive] sub error', err),
      complete: () => console.debug('[StationLive] sub complete')
    });
  }


  ngOnDestroy(): void {
    this.sub?.unsubscribe();
    this.cmdWatering('stop')
  }

  goNextStep() {
    this.stepper.next();
  }

  cancelExpressAnalysis() {
    this.reportId = null;
    this.cdr.markForCheck();
    this.cmdWatering('stop')
  }


  private pushMessage(msg: any) {
    if(msg.type === "data") {
      this.data = { ts: Date.now(), raw: msg.data } ;
    } else {
      this.message = msg;
    }
    this.cdr.markForCheck();
  }

  onStepChange(event: StepperSelectionEvent) {
    const index = event.selectedIndex;
    const last_index = event.previouslySelectedIndex;

    switch (last_index) {
      case StepIndex.EXPRESS_ANALYSIS:
        if(index !== StepIndex.PRESENT_RESULTS) {
          this.reportId = null;
        }
        this.cmdWatering('stop')
        break;
      case StepIndex.TEST_SENSORS:
        this.sensorTest('stop')
        break;
      case StepIndex.PRESENT_RESULTS:
        this.reportDeleted = true;
        this.reportId = null;
        break;
    }

    switch (index) {
      case StepIndex.TEST_SENSORS:
        this.sensorTest('start')
        break;

      case StepIndex.EXPRESS_ANALYSIS:
        this.cmdWatering('start')
        this.reportDeleted = false;
        break;

      default:
        console.warn("Étape inconnue");
        break;
    }
  }

  sensorTest(action: string): void {
    this.isTestingSensor = action !== 'stop';

    this.cdr.markForCheck();

    const body = {
      type: 'send_all_data',
      action: action,
      plant_id: this.plantId,
      duration: this.TEST_SENSORS_DURATION
    };

    if(action === "start") {
      this.resetGraph()
    } else {
      this.numberOfDataMessages = 0;
    }

    const stationId = this.activeStationMacAddress();
    if (!stationId) {
      console.error('No active station MAC address');
      return;
    }

    this.stationService.sendCommand(stationId, body).subscribe({
      next: (res) => {
        console.debug('Command response', res);
        this.pushMessage(res ?? { message: 'Command sent' });
      },
      error: (err) => {
        console.error('Failed to send command', err);
        this.pushMessage({ error: 'Failed to send command' });
      },
      complete: () => {
        this.cdr.markForCheck();
      }
    });
  }

  resetGraph() {
    this.seriesService.setInitialSeries([
      { name: 'Soil humidity', data: [] },
      { name: 'Pump', data: [] },
      { name: 'Target Humidity', data: [] },
    ]);
  }

  async restartAnalysis() {
    this.stepper.selectedIndex = StepIndex.EXPRESS_ANALYSIS;
  }

  async deleteReport() {
    const reportId = this.reportId;
    if(reportId === null)  {
      console.log("The report id is null")
      return
    }

    try {
      await this.stationService.deleteWateringReport(reportId);
      console.log(`Deleted the report with id ${reportId}`);
      this.reportDeleted = true;
      this.reportId = null;
      this.cdr.markForCheck();
      // this.snackbar.open("Rapport supprimé", "Fermer", { duration: 3000 });
    } catch (error) {
      console.error("Erreur suppression :", error);
      // this.snackbar.open("Échec de la suppression", "Fermer", { duration: 3000 });
    }
  }

  cmdWatering(action: string): void {
    this.isExpressAnalysis = action !== 'stop';
    this.cdr.markForCheck();

    const body = {
      type: 'watering',
      action: action,
      plant_id: this.plantId,
      duration: this.EXPRESS_ANALYSIS_DURATION
    };

    if(action === "start") {
      this.resetGraph()
    } else {
        this.numberOfDataMessages = 0;
    }

    const stationId = this.activeStationMacAddress();
    if (!stationId) {
      console.error('No active station MAC address');
      return;
    }

    this.stationService.sendCommand(stationId, body).subscribe({
      next: (res) => {
        console.debug('Command response', res);
        this.pushMessage(res ?? { message: 'Command sent' });
      },
      error: (err) => {
        console.error('Failed to send command', err);
        this.pushMessage({ error: 'Failed to send command' });
      },
      complete: () => {
        this.cdr.markForCheck();
      }
    });
  }
}
