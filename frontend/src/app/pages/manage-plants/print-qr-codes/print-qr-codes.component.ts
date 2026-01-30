import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButton } from '@angular/material/button';
import { MatIcon } from '@angular/material/icon';
import { Router } from '@angular/router';

@Component({
  selector: 'app-print-qr-codes',
  standalone: true,
  imports: [CommonModule, MatButton, MatIcon],
  templateUrl: './print-qr-codes.component.html',
  styleUrls: ['./print-qr-codes.component.scss']
})
export class PrintQrCodesComponent implements OnInit {
  qrCodes: Array<{ id: number; name: string; qrCodeDataUrl: string }> = [];

  constructor(private router: Router) {
    // Récupérer les données depuis navigation state
    const navigation = this.router.getCurrentNavigation();
    if (navigation?.extras.state) {
      this.qrCodes = navigation.extras.state['qrCodes'] || [];
    }
  }

  ngOnInit() {
    // Auto-print après un court délai pour que le DOM soit prêt
    setTimeout(() => {
      // window.print();
    }, 500);
  }

  print() {
    window.print();
  }

  close() {
    window.history.back();
  }
}
