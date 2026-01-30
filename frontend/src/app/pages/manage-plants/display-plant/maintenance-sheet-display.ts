import {Component, EventEmitter, Input, OnChanges, Output, SimpleChanges} from '@angular/core';
import { MatIcon } from '@angular/material/icon';
import {DatePipe, NgIf} from '@angular/common';
import { DomSanitizer, SafeUrl } from '@angular/platform-browser';
import * as QRCode from 'qrcode';
import {MatButton} from '@angular/material/button';

@Component({
  selector: 'app-maintenance-sheet-display',
  templateUrl: './maintenance-sheet-display.html',
  imports: [
    MatIcon,
    DatePipe,
    NgIf,
    MatButton,
  ],
  standalone: true,
  styleUrls: ['./maintenance-sheet-display.scss']
})
export class MaintenanceSheetDisplayComponent implements OnChanges {
  @Input() sheet: any;
  qrCodeDataUrl: string | null = null;
  @Output() delete = new EventEmitter<number>();


  constructor(private sanitizer: DomSanitizer) {}

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['sheet'] && this.sheet?.id) {
      this.generateQRCode();
    }
  }

  async generateQRCode(): Promise<void> {
    try {
      const qrData = `plant/${this.sheet.id}`;
      this.qrCodeDataUrl = await QRCode.toDataURL(qrData, {
        width: 200,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });
    } catch (error) {
      console.error('Erreur lors de la génération du QR code:', error);
      this.qrCodeDataUrl = null;
    }
  }

  getPhotoUrl(): SafeUrl | null {
    if (!this.sheet?.photo_base64) {
      return null;
    }
    // Si c'est déjà au format data:image, retourner tel quel
    if (this.sheet.photo_base64.startsWith('data:image')) {
      return this.sanitizer.bypassSecurityTrustUrl(this.sheet.photo_base64);
    }
    // Sinon, ajouter le préfixe data:image/jpeg;base64,
    return this.sanitizer.bypassSecurityTrustUrl(`data:image/jpeg;base64,${this.sheet.photo_base64}`);
  }

  /**
   * Format large numbers with k suffix (e.g., 3500 → 3.5k)
   */
  formatNumber(value: number | undefined | null): string {
    if (!value) return '0';
    if (value >= 1000) {
      return (value / 1000).toFixed(1).replace(/\.0$/, '') + 'k';
    }
    return value.toString();
  }
}
