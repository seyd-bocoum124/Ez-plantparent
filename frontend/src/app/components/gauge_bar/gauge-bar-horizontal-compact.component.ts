import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-gauge-bar-horizontal-compact',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './gauge-bar-horizontal-compact.component.html',
  styleUrls: ['./gauge-bar-horizontal-compact.component.scss']
})
export class GaugeBarHorizontalCompactComponent {
  @Input() min: number = 0;
  @Input() max: number = 100;
  @Input() target: number = 50;
  @Input() measured: number = 50;
  @Input() scaleMin: number = 0;
  @Input() scaleMax: number = 100;
  @Input() unit: string = '';

  getPosition(value: number): number {
    const range = this.scaleMax - this.scaleMin;
    return ((value - this.scaleMin) / range) * 100;
  }

  getMinPosition(): number {
    return this.getPosition(this.min);
  }

  getMaxPosition(): number {
    return this.getPosition(this.max);
  }

  getTargetPosition(): number {
    return this.getPosition(this.target);
  }

  getMeasuredPosition(): number {
    return this.getPosition(this.measured);
  }

  getRangeWidth(): number {
    return this.getMaxPosition() - this.getMinPosition();
  }
}
