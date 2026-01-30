import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-gauge-bar',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './gauge-bar.component.html',
  styleUrls: ['./gauge-bar.component.scss']
})
export class GaugeBarComponent {
  @Input() min: number = 0;
  @Input() max: number = 100;
  @Input() target: number = 50;
  @Input() measured: number = 40;
  @Input() scaleMin: number = 0;
  @Input() scaleMax: number = 100;
  @Input() minLabel: string = 'Min';
  @Input() maxLabel: string = 'Max';
  @Input() targetLabel: string = 'Target';
  @Input() measuredLabel: string = 'Measured';
  @Input() unit: string = '';

  /**
   * Calcule la position en pourcentage pour une valeur donnée
   */
  getPosition(value: number): number {
    const range = this.scaleMax - this.scaleMin;
    if (range === 0) return 0;
    const position = ((value - this.scaleMin) / range) * 100;
    return Math.max(0, Math.min(100, position));
  }

  /**
   * Calcule la largeur de la zone verte (min-max)
   */
  getGreenZoneWidth(): number {
    return this.getPosition(this.max) - this.getPosition(this.min);
  }

  /**
   * Calcule la position de départ de la zone verte
   */
  getGreenZoneStart(): number {
    return this.getPosition(this.min);
  }
}
