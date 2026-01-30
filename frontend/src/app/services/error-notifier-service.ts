import {MaintenanceSheetService} from './maintenance-sheets.service';
import {MatSnackBar} from '@angular/material/snack-bar';
import {effect, Injectable} from '@angular/core';
import * as _ from 'lodash';

@Injectable({ providedIn: 'root' })
export class ErrorNotifierService {
  constructor(private snackBar: MatSnackBar, private sheetService: MaintenanceSheetService) {
    effect(() => {
      const errors = this.sheetService.errors();
      if (errors.load) {
        this.snackBar.open(JSON.stringify(errors.load), 'Fermer', { duration: 3000 });
      }
      if (errors.delete) {
        const errorMessage = "Erreur de suppression: " + _.get(errors.delete, "error.detail", "")
        this.snackBar.open(errorMessage, 'Fermer', { duration: 3000 });
      }
      if (errors.create) {
        this.snackBar.open(JSON.stringify(errors.create), 'Fermer', { duration: 3000 });
      }
    });
  }
}
