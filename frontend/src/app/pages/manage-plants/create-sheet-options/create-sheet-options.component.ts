import { Component } from '@angular/core';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { RouterLink } from '@angular/router';
import { MatBottomSheetRef } from '@angular/material/bottom-sheet';

@Component({
  selector: 'app-create-sheet-options',
  standalone: true,
  imports: [MatListModule, MatIconModule, RouterLink],
  templateUrl: './create-sheet-options.component.html',
  styleUrls: ['./create-sheet-options.component.scss']
})
export class CreateSheetOptionsComponent {
  constructor(private bottomSheetRef: MatBottomSheetRef<CreateSheetOptionsComponent>) {}

  close() {
    this.bottomSheetRef.dismiss();
  }
}
