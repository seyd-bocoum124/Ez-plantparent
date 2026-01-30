import {ChangeDetectorRef, Component, ViewChild} from '@angular/core';
import {FormBuilder, FormGroup, Validators, ReactiveFormsModule, FormsModule} from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import {GbifService} from '../../../services/gbif.service';
import {
  MatCard,
  MatCardActions,
  MatCardContent,
  MatCardHeader,
  MatCardTitle
} from '@angular/material/card';
import {MaintenanceSheetService} from '../../../services/maintenance-sheets.service';
import {RouterLink} from '@angular/router';
import {MatStep, MatStepLabel, MatStepper} from '@angular/material/stepper';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {MaintenanceSheetDisplayComponent} from '../display-plant/maintenance-sheet-display';
import {StepperSelectionEvent} from '@angular/cdk/stepper';
import {PlantNamingFormComponent} from './plant-name-form/component';
import {BreadcrumbService} from '../../../services/breadcrumb.service';

enum IdentificationStage {
  FILLING_SCIENTIFIC_NAME = 1,
  DISPLAY_SUGGESTIONS = 3,
  SUGGESTION_CHOSEN = 4,
  GIVE_A_NAME = 5,
  WAIT_MAINTENANCE_SHEET = 6,
  MAINTENANCE_SHEET_SUCCESS = 7,
  MAINTENANCE_SHEET_DELETED = 8,
}

enum StepIndex {
  IDENTIFY_PLANT = 0,
  GIVE_A_NAME = 1,
  PRESENT_RESULTS = 2,
}

@Component({
  selector: 'app-create-maintenance-sheet',
  standalone: true,
  templateUrl: './create-maintenance-sheet.html',
  styleUrls: ['./create-maintenance-sheet.scss'],
  imports: [
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    FormsModule,
    MatCard,
    MatCardTitle,
    RouterLink,
    MatStepper,
    MatStep,
    MatStepLabel,
    MatProgressSpinnerModule,
    MatCardHeader,
    MatCardContent,
    MatCardActions,
    MaintenanceSheetDisplayComponent,
    PlantNamingFormComponent,
  ]
})
export class CreateMaintenanceSheet {
  form: FormGroup;
  inputName = '';
  result: any | null = null;
  selected: any | null = null;
  newMaintenanceSheet: any | null = null;
  isWaiting: boolean = false
  readonly MAINTENANCE_SHEET_SUCCESS_DURATION = 3000;

  @ViewChild('stepper') stepper!: MatStepper;
  currentStepIndex = StepIndex.IDENTIFY_PLANT;
  identificationStage : IdentificationStage = IdentificationStage.FILLING_SCIENTIFIC_NAME;


  constructor(
    private fb: FormBuilder,
    private gbifService: GbifService,
    private maintenanceSheetService: MaintenanceSheetService,
    private cdr: ChangeDetectorRef,
    private breadcrumbService: BreadcrumbService
  ) {
    this.form = this.fb.group({
    name: [
          '',
          [Validators.required, Validators.maxLength(50)],
          []
        ]
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
      {label: 'Plantes', routerLink: ['/my-plants'],
        childs: [
          {label: 'Créer par photo', routerLink: ['/my-plants/create/from-picture']},
          {label: 'Créer par nom', routerLink: ['/my-plants/create']},
        ]
      },
      { label: 'Créer par nom' },
    ]);
  }

  goNextStep() {
    this.currentStepIndex++;
    if(this.stepper && this.stepper.selected)
      this.stepper.selected.completed = true;
    this.stepper.next();
    this.cdr.markForCheck();
  }

  onStepChange(event: StepperSelectionEvent) {
    const index = event.selectedIndex;
    switch (index) {
      case StepIndex.IDENTIFY_PLANT:
        this.identificationStage = IdentificationStage.SUGGESTION_CHOSEN;
        break;
      case StepIndex.GIVE_A_NAME:
        this.identificationStage = IdentificationStage.GIVE_A_NAME;
        break;
    }

    this.cdr.markForCheck();
  }

  isStepPassed(step: StepIndex): boolean {
    return this.currentStepIndex > step;
  }

  isBefore(step: StepIndex): boolean {
    return this.currentStepIndex < step;
  }

  onNameSubmitted(event: any) {
      const name = event.name;
      const photo = event.photo;

      this.identificationStage = IdentificationStage.WAIT_MAINTENANCE_SHEET;
      this.isWaiting = true;
      this.maintenanceSheetService.createMaintenanceSheet({
        ...this.selected,
        "name": name,
        "photo_base64": photo
      }).subscribe({
        next: (res) => {
          this.newMaintenanceSheet = res;
          this.isWaiting = false;
          this.identificationStage = IdentificationStage.MAINTENANCE_SHEET_SUCCESS;
          this.cdr.detectChanges();
          setTimeout(()=>  {
            this.goNextStep();
          }, this.MAINTENANCE_SHEET_SUCCESS_DURATION);
        },
        error: (err) => {
          this.cdr.detectChanges();
          console.error('Erreur création de fiche', err)
        }
      });
  }

  searchSuggestions() {
    this.cdr.detectChanges();
    this.gbifService.speciesSearch(this.inputName).subscribe({
      next: (res) => {
        console.log("Resultats!!!!");
        console.log(res);
        this.result = res;
        this.identificationStage = IdentificationStage.DISPLAY_SUGGESTIONS;
        this.cdr.detectChanges();
      },
      error: (err) => console.error('Erreur GBIF', err)
    });
  }

  getFilteredNames(item: any): { vernacularName: string; language: string }[] {
  return item.vernacularNames?.filter((v: { vernacularName: string; language: string }) =>
      ['fra', 'eng'].includes(v.language)
    ) ?? [];
  }

  async deleteMaintenanceSheet(id:number) {
    await this.maintenanceSheetService.deleteMaintenanceSheet(id);
    this.newMaintenanceSheet = null;
    this.identificationStage = IdentificationStage.MAINTENANCE_SHEET_DELETED;
    this.cdr.detectChanges();
  }

  goToFillSuggestion() {
    this.identificationStage = IdentificationStage.FILLING_SCIENTIFIC_NAME;
    this.cdr.detectChanges();
  }



  selectItem(i: number) {
    let selected = this.result?.results?.[i] ?? null;
    this.selected = {
      'scientific_name' : selected.scientificName,
      'taxonkey': selected.taxonID ?? null,
      'taxon_rank': selected.rank ?? null,
      "identification_source": "GBIF",
      "common_name": getPreferredCommonName(selected.vernacularNames)
    };
    this.identificationStage = IdentificationStage.SUGGESTION_CHOSEN;
    this.cdr.detectChanges();
  }

  protected readonly IdentificationStage = IdentificationStage;
  protected readonly StepIndex = StepIndex;
}

function getPreferredCommonName(list: { vernacularName: string; language: string }[]): string | null {
    return (
      list.find(it => it.language === 'fra')?.vernacularName ??
      list.find(it => it.language === 'eng')?.vernacularName ??
      list[0]?.vernacularName ??
      null
    );
  }

