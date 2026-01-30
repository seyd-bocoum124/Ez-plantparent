import { Component, OnInit, signal } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormBuilder, FormGroup, Validators, ReactiveFormsModule } from '@angular/forms';
import {Station, StationService} from '../../services/station.service';



@Component({
  selector: 'app-pair-station',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule],
  templateUrl: './component.html',
  styleUrls: ['./component.scss'],
})
export class PairStationComponent implements OnInit {

  stations = signal<Station[]>([]);
  selected: number | null = null;
  pairingForm: FormGroup;
  isLoading = signal<boolean>(false);
  pairingMessage = signal<string>('');
  pairingSuccess = signal<boolean>(false);

  constructor(
    private stationService: StationService,
    private fb: FormBuilder
  ) {
    this.pairingForm = this.fb.group({
      pairingCode: ['', [Validators.required, Validators.maxLength(12)]]
    });
  }

  ngOnInit() {
    this.loadStations();
  }

  loadStations() {
    this.stationService.getStations().subscribe((data: Station[]) => {
      this.stations.set(data);
    });
  }

  onPairStation() {
    if (this.pairingForm.invalid) {
      return;
    }

    this.isLoading.set(true);
    this.pairingMessage.set('');

    const pairingCode = this.pairingForm.get('pairingCode')?.value;

    this.stationService.pairStation(pairingCode).subscribe({
      next: () => {
        this.pairingSuccess.set(true);
        this.pairingMessage.set('Station pairée avec succès!');
        this.pairingForm.reset();
        this.isLoading.set(false);
        // Recharger la liste des stations
        this.loadStations();
      },
      error: (err) => {
        this.pairingSuccess.set(false);
        this.pairingMessage.set(err.error?.detail || 'Erreur lors du pairing');
        this.isLoading.set(false);
      }
    });
  }

  trackById(_index: number, item: Station) {
    return item.id;
  }
}

