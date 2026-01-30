import {
  Component, OnInit, AfterViewInit, QueryList, ViewChildren, ElementRef, signal, Inject, ViewChild, effect
} from '@angular/core';
import { CommonModule } from '@angular/common';
import { StationService } from '../../../services/station.service';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import { BarcodeScanner, BarcodeFormat } from '@capacitor-mlkit/barcode-scanning';
import { MatToolbar } from "@angular/material/toolbar";
import { MatIcon } from '@angular/material/icon';
import { MatButton, MatFabButton, MatIconButton } from "@angular/material/button";
import { InViewportModule } from 'ng-in-viewport';
import { NativeService } from "../../../services/native.service";
import { RouterLink, ActivatedRoute, Router } from "@angular/router";
import {BreadcrumbService} from '../../../services/breadcrumb.service';
import {GaugeBarHorizontalCompactComponent} from '../../../components/gauge_bar/gauge-bar-horizontal-compact.component';
import {MatMenu, MatMenuItem, MatMenuTrigger} from '@angular/material/menu';
import {MatBottomSheet} from '@angular/material/bottom-sheet';
import {MatDivider} from '@angular/material/divider';
import {MaintenanceActionsSheet} from './maintenance-actions-sheet/component';

enum Watering_status { URGENT_WATERING = "under_min_humidity" }

@Component({
  selector: 'app-pair-station',
  standalone: true,
  imports: [
    CommonModule,
    MatToolbar,
    MatIcon,
    MatFabButton,
    MatIconButton,
    InViewportModule,
    MatButton,
    RouterLink,
    GaugeBarHorizontalCompactComponent,
    MatMenuTrigger,
    MatMenu,
    MatMenuItem,
    MatDivider,
  ],
  templateUrl: './component.html',
  styleUrls: ['./component.scss'],
})
export class ViewDailyScheduleComponent implements OnInit, AfterViewInit {

  maintenanceSchedules = signal<any[]>([]);
  Watering_status = Watering_status;
  qrcode = "";
  currentPlantIndex = 0;
  private isManualScrolling = false;
  isNativePlatform: boolean;
  private targetPlantId: number | null = null;

  @ViewChildren('plantElement') plantElements!: QueryList<ElementRef>;

  constructor(
    private stationService: StationService,
    private sanitizer: DomSanitizer,
    private nativeService: NativeService,
    private route: ActivatedRoute,
    private breadcrumbService: BreadcrumbService,
    private bottomSheet: MatBottomSheet,
    private router: Router
  ) {
    this.isNativePlatform = this.nativeService.isNative();

    effect(() => {
      const schedules = this.maintenanceSchedules();
      if (schedules.length > 0 && this.targetPlantId !== null) {
        setTimeout(() => {
          this.scrollToPlantById(this.targetPlantId!);
          this.targetPlantId = null;
        }, 200);
      }
    });
  }

  ngOnInit() {
    this.breadcrumbService.setItems([
      { label: 'Accueil', routerLink: ['/accueil'],
        childs: [
          {label: 'Maintenance', routerLink: ['/maintenance-schedule']},
          {label: 'Plantes', routerLink: ['/my-plants']},
        ]
      },
      { label: 'Maintenance'},
    ]);

    this.route.queryParams.subscribe(params => {
      const plantId = params['plantId'];
      if (plantId) {
        console.log(plantId);
        this.targetPlantId = Number(plantId);
      }
    });

    this.loadStations();
  }

  ngAfterViewInit() {
    // L'effect dans le constructor gère le scroll
  }

  loadStations() {
    this.stationService.getDailyMaintenanceSchedules().subscribe((schedules: any[]) => {
      this.maintenanceSchedules.set(schedules);
    });
  }

  onPlantInViewport(event: { visible: boolean }, index: number): void {
    if (event.visible && !this.isManualScrolling) {
      this.currentPlantIndex = index;
    }
  }

  getPhotoUrl(sheet:any): SafeUrl | null {
    if (!sheet.photo_base64) {
      return null;
    }

    if (sheet.photo_base64.startsWith('data:image')) {
      return this.sanitizer.bypassSecurityTrustUrl(sheet.photo_base64);
    }

    return this.sanitizer.bypassSecurityTrustUrl(`data:image/jpeg;base64,${sheet.photo_base64}`);
  }

  scrollToPlantById(plantId: number): void {
    const elements = this.plantElements.toArray();
    const targetIndex = elements.findIndex(el =>
      el.nativeElement.getAttribute('data-plant-id') === plantId.toString()
    );

    if (targetIndex !== -1) {
      this.scrollToElement(elements, targetIndex);
    }
  }

  async scanQRCode(): Promise<void> {
    try {
      const { camera } = await BarcodeScanner.requestPermissions();

      if (camera !== 'granted') {
        alert('Permission caméra refusée');
        return;
      }

      const result = await BarcodeScanner.scan({
        formats: [BarcodeFormat.QrCode]
      });

      if (result.barcodes.length > 0) {
        const qrCodeUrl = result.barcodes[0].displayValue;
        this.qrcode = qrCodeUrl;

        const id = qrCodeUrl.split("/")[1];

        if (id) {
          const plantId = Number(id);
          this.scrollToPlantById(plantId);
        } else {
          alert(`QR Code scanné: ${qrCodeUrl}`);
        }
      }
    } catch (error) {
      console.error('Erreur lors du scan:', error);
      alert('Erreur lors du scan du QR code');
    }
  }

  displayMeasureTimeContext(days:any, hour:any, measure:any) {
    if(days == null) {
      return "Non mesuré"
    } else if (days < 1) {
      return `${measure} ll y a ${hour} h`;
    } else {
      return `${measure} il y a ${days} jour(s)`;
    }
  }

  nextItem(): void {
    const elements = this.plantElements.toArray();
    if (elements.length === 0) return;

    const newIndex = (this.currentPlantIndex + 1) % elements.length;

    this.scrollToElement(elements, newIndex);

    this.isManualScrolling = true;
    this.currentPlantIndex = newIndex;
  }


  private scrollToElement(elements: ElementRef[], newIndex: number) {
    this.isManualScrolling = true;
    this.currentPlantIndex = newIndex;

    const el = elements[newIndex].nativeElement as HTMLElement;

    // Calcul position absolue de l'élément
    const elementTop = el.offsetTop;
    const offset = 70; // Espace pour le menu

    window.scrollTo({
      top: elementTop - offset,
      behavior: 'smooth'
    });

    setTimeout(() => this.isManualScrolling = false, 1000);
  }




  previousItem(): void {
    const elements = this.plantElements.toArray();
    if (elements.length === 0) return;
    const newIndex = (this.currentPlantIndex - 1 + elements.length) % elements.length;

    this.scrollToElement(elements, newIndex);
  }

  openMaintenanceActions(plantId: number): void {
    const bottomSheetRef = this.bottomSheet.open(MaintenanceActionsSheet, {
      data: { plantId }
    });

    bottomSheetRef.afterDismissed().subscribe(action => {
      if (action) {
        this.router.navigate(action.route);
      }
    });
  }
}


