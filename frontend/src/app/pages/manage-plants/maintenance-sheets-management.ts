import {Component, effect, ViewChild} from '@angular/core';
import {MaintenanceSheetService} from '../../services/maintenance-sheets.service';
import {Router, RouterLink} from '@angular/router';
import {MaintenanceSheetDisplayComponent} from './display-plant/maintenance-sheet-display';
import {MatButton} from '@angular/material/button';
import {MatSnackBar} from '@angular/material/snack-bar';
import * as QRCode from 'qrcode';
import {MatIcon} from '@angular/material/icon';
import {MatMenu, MatMenuItem, MatMenuTrigger} from '@angular/material/menu';
import {MatBottomSheet} from '@angular/material/bottom-sheet';
import {CreateSheetOptionsComponent} from './create-sheet-options/create-sheet-options.component';
import {NativeService} from '../../services/native.service';
import { MatMenuModule } from '@angular/material/menu';
import {BreadcrumbService} from '../../services/breadcrumb.service';


@Component({
  selector: 'app-maintenance-sheets-management',
  imports: [
    RouterLink,
    MaintenanceSheetDisplayComponent,
    MatButton,
    MatIcon,
    MatMenu,
    MatMenuItem,
    MatMenuTrigger,
    MatMenuModule
  ],

  templateUrl: './maintenance-sheets-management.html',
  styleUrl: './maintenance-sheets-management.scss'
})
export class MaintenanceSheetsManagement {
  constructor(
    private maintenanceSheetService: MaintenanceSheetService,
    private snackBar: MatSnackBar,
    private bottomSheet: MatBottomSheet,
    private nativeService: NativeService,
    private router: Router,
    private breadcrumbService: BreadcrumbService
  ) {
    this.isNativePlatform = this.nativeService.isNative();
  }
  @ViewChild(MatMenuTrigger) menuTrigger!: MatMenuTrigger;



  isNativePlatform: boolean;


  openCreateMenu() {
  if (this.isNativePlatform) {
      this.bottomSheet.open(CreateSheetOptionsComponent);
    } else {
      this.menuTrigger.openMenu();
    }
  }


  get sheets() {
    return this.maintenanceSheetService.sheets;
  }

  async ngOnInit() {
    this.breadcrumbService.setItems([
      { label: 'Accueil', routerLink: ['/accueil'],
        childs: [
          {label: 'Maintenance', routerLink: ['/maintenance-schedule']},
          {label: 'Plantes', routerLink: ['/my-plants']},
        ]
      },
      {label: 'Plantes', routerLink: ['/my-plants'],
        childs: [
          {label: 'Créer par photo', routerLink: ['/my-plants/create/from-picture']},
          {label: 'Créer par nom', routerLink: ['/my-plants/create']},
        ]
      },
    ]);
    await this.maintenanceSheetService.loadMaintenanceSheets();
  }

  async deleteMaintenanceSheet(id:number) {
    await this.maintenanceSheetService.deleteMaintenanceSheet(id);
    this.snackBar.open("Plante Supprimée avec succès", 'Fermer', { duration: 3000 });
  }

  async printAllQRCodes() {
    const sheets = this.sheets();
    if (sheets.length === 0) {
      this.snackBar.open('Aucune fiche à imprimer', 'Fermer', { duration: 3000 });
      return;
    }

    // Generate all QR codes
    const qrCodesPromises = sheets.map(async (sheet) => {
      const qrData = `plant/${sheet.id}`;
      const qrCodeDataUrl = await QRCode.toDataURL(qrData, {
        width: 300,
        margin: 2,
        color: { dark: '#000000', light: '#FFFFFF' }
      });
      return {
        id: sheet.id,
        name: sheet.name || sheet.common_name || `Plante ${sheet.id}`,
        qrCodeDataUrl
      };
    });

    const qrCodes = await Promise.all(qrCodesPromises);

    // Navigate to print component with data
    await this.router.navigate(['/my-plants/print-qr'], {
      state: { qrCodes }
    });
  }

  async printAllQRCodesOld() {
    const sheets = this.sheets();
    if (sheets.length === 0) {
      this.snackBar.open('Aucune fiche à imprimer', 'Fermer', { duration: 3000 });
      return;
    }

    // Generate all QR codes
    const qrCodesPromises = sheets.map(async (sheet) => {
      const qrData = `plant/${sheet.id}`;
      const qrCodeDataUrl = await QRCode.toDataURL(qrData, {
        width: 300,
        margin: 2,
        color: { dark: '#000000', light: '#FFFFFF' }
      });
      return {
        id: sheet.id,
        name: sheet.name || sheet.common_name || `Plante ${sheet.id}`,
        qrCodeDataUrl
      };
    });

    const qrCodes = await Promise.all(qrCodesPromises);

    // Create print content
    const printContent = `
      <!DOCTYPE html>
      <html>
      <head>
        <title>QR Codes - Fiches d'entretien</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
          @media print {
            @page { margin: 1cm; }
            body { margin: 0; }
            .no-print { display: none; }
          }
          body {
            font-family: Arial, sans-serif;
            padding: 20px;
          }
          .header-buttons {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            flex-wrap: wrap;
          }
          .header-buttons button {
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border: 1px solid #333;
            border-radius: 4px;
            background: white;
          }
          .close-btn {
            background: #f44336 !important;
            color: white !important;
            border-color: #f44336 !important;
          }
          .qr-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, 3cm);
            gap: 0.5cm;
            justify-content: start;
          }
          .qr-item {
            width: 3cm;
            height: 5cm;
            border: 1px solid #333;
            padding: 0.2cm;
            text-align: center;
            break-inside: avoid;
            page-break-inside: avoid;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-sizing: border-box;
          }
          .qr-item img {
            width: 2.5cm;
            height: 2.5cm;
            object-fit: contain;
          }
          .qr-item h3 {
            margin: 0.1cm 0 0 0;
            font-size: 8pt;
            font-weight: bold;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            width: 100%;
          }
          .qr-item p {
            margin: 0;
            font-size: 6pt;
            color: #666;
          }
        </style>
      </head>
      <body>
        <h1>Codes QR - Fiches d'entretien</h1>
        <div class="header-buttons no-print">
          <button onclick="window.print()">Imprimer</button>
          <button class="close-btn" onclick="window.close(); window.location.href='about:blank';">Fermer</button>
        </div>
        <div class="qr-grid">
          ${qrCodes.map(qr => `
            <div class="qr-item">
              <img src="${qr.qrCodeDataUrl}" alt="QR Code ${qr.name}" />
              <h3>${qr.name}</h3>
              <p>plant/${qr.id}</p>
            </div>
          `).join('')}
        </div>
      </body>
      </html>
    `;

    // Open new window and print
    const printWindow = window.open('', '_blank', 'width=800,height=600');
    if (printWindow) {
      printWindow.document.write(printContent);
      printWindow.document.close();
      printWindow.focus();

      // Wait for images to load before printing
      printWindow.onload = () => {
        setTimeout(() => {
          printWindow.print();
        }, 250);
      };
    } else {
      this.snackBar.open('Impossible d\'ouvrir la fenêtre d\'impression', 'Fermer', { duration: 3000 });
    }
  }
}
