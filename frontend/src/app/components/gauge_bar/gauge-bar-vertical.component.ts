import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-gauge-bar-vertical',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './gauge-bar-vertical.component.html',
  styleUrls: ['./gauge-bar-vertical.component.scss']
})
export class GaugeBarVerticalComponent {
  @Input() min: number = 0;
  @Input() max: number = 100;
  @Input() target: number = 50;
  @Input() measured: number = 40;
  @Input() scaleMin: number = 0;
  @Input() scaleMax: number = 100;
  @Input() unit: string = '';

  /**
   * Calcule la position en pourcentage pour une valeur donnée (du bas vers le haut)
   */
  getPosition(value: number): number {
    const range = this.scaleMax - this.scaleMin;
    if (range === 0) return 0;
    const position = ((value - this.scaleMin) / range) * 100;
    return Math.max(0, Math.min(100, position));
  }

  /**
   * Calcule la hauteur de la zone verte (min-max)
   */
  getGreenZoneHeight(): number {
    return this.getPosition(this.max) - this.getPosition(this.min);
  }

  /**
   * Calcule la position de départ de la zone verte (du bas)
   */
  getGreenZoneBottom(): number {
    return this.getPosition(this.min);
  }
}
