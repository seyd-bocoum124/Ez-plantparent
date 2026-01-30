import {ChangeDetectorRef, Component, signal, ViewChild} from '@angular/core';
import {MaintenanceSheetService} from '../../../services/maintenance-sheets.service';
import {MatButton, MatFabButton} from '@angular/material/button';
import {NgForOf, PercentPipe} from '@angular/common';
import * as _ from 'lodash';
import {MatStep, MatStepLabel, MatStepper} from '@angular/material/stepper';
import {RouterLink} from '@angular/router';
import {MatProgressSpinnerModule} from '@angular/material/progress-spinner';
import {StepperSelectionEvent} from '@angular/cdk/stepper';
import {PlantNamingFormComponent} from '../create-plant-by-name/plant-name-form/component';
import {MaintenanceSheetDisplayComponent} from '../display-plant/maintenance-sheet-display';
import {DomSanitizer, SafeUrl} from '@angular/platform-browser';
import {MatIcon} from '@angular/material/icon';
import {CameraComponent} from '../../../components/camera/component';
import {BreadcrumbService} from '../../../services/breadcrumb.service';

export enum IdentificationStage {
  TAKING_PICTURES = 1,
  WAIT_SUGGESTIONS = 2,
  DISPLAY_SUGGESTIONS = 3,
  SUGGESTION_CHOSEN = 4,
  GIVE_A_NAME = 5,
  WAIT_MAINTENANCE_SHEET = 6,
}

enum StepIndex {
  TAKE_PICTURE = 0,
  SELECT_SUGGESTION = 1,
  GIVE_A_NAME = 2,
  PRESENT_RESULTS = 3,
}

interface PlantSuggestion {
  commonNames: string[];
  scientificNameWithoutAuthor: string;
  scientificName: string;
  gbif?: string;
  score: number;
  images: {
    timestamp: number;
    organ: string;
    url: string;
  }[];
}

@Component({
  selector: 'create-maintenance-sheet-by-picture',
  standalone: true,
  templateUrl: './component.html',
  imports: [
    MatButton,
    MatFabButton,
    MatIcon,
    PercentPipe,
    NgForOf,
    MatStepper,
    MatStep,
    MatStepLabel,
    RouterLink,
    MatProgressSpinnerModule,
    PlantNamingFormComponent,
    MaintenanceSheetDisplayComponent,
    CameraComponent,
  ],
  styleUrl: './component.scss'
})
export class CreateMaintenanceSheetByPictureComponent {
  newMaintenanceSheet: any | null = null;
  selected: PlantSuggestion | null = null;
  createdName?: string;


  @ViewChild(CameraComponent) camera!: CameraComponent;
  @ViewChild('stepper') stepper!: MatStepper;
  photos: string[] = [];
  showFlash = false;

  suggestions: PlantSuggestion[] = [];
  currentStepIndex = StepIndex.TAKE_PICTURE;
  identificationStage: IdentificationStage = IdentificationStage.TAKING_PICTURES;

  constructor(
    private maintenanceSheetService: MaintenanceSheetService,
    private cdr: ChangeDetectorRef,
    private sanitizer: DomSanitizer,
    private breadcrumbService: BreadcrumbService
  ) {
  }

  getSafeUrl(url: string): SafeUrl {
    return this.sanitizer.bypassSecurityTrustUrl(url);
  }


  ngOnInit() {
    // this.breadcrumbService.setItems([
    //   {label: 'Accueil', routerLink: ['/accueil']},
    //   {label: 'Plantes', routerLink: ['/my-plants']},
    //   {label: 'Créer par photo'},
    // ]);

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
      {label: 'Créer par photo'},
    ]);
  }

  goNextStep() {
    this.currentStepIndex++;
    if (this.stepper && this.stepper.selected)
      this.stepper.selected.completed = true;
    this.stepper.next();
    this.cdr.markForCheck();
  }

  isStepPassed(step: StepIndex): boolean {
    return this.currentStepIndex > step;
  }

  isBefore(step: StepIndex): boolean {
    return this.currentStepIndex < step;
  }

  onStepChange(event: StepperSelectionEvent) {
    const index = event.selectedIndex;
    switch (index) {
      case StepIndex.TAKE_PICTURE:
        this.identificationStage = IdentificationStage.TAKING_PICTURES;
        break;
      case StepIndex.SELECT_SUGGESTION:
        this.identificationStage = IdentificationStage.DISPLAY_SUGGESTIONS;
        break;
      case StepIndex.GIVE_A_NAME:
        this.identificationStage = IdentificationStage.GIVE_A_NAME;
    }

    if (index === StepIndex.SELECT_SUGGESTION && this.selected) {
      this.identificationStage = IdentificationStage.SUGGESTION_CHOSEN;
    }

    this.cdr.markForCheck();
  }

  onPhotosUpdate(updated: string[]) {
    this.photos = updated;
  }

  removePhoto(index: number) {
    this.photos.splice(index, 1);
  }

  onVideoTap() {
    // Prendre une photo quand on tap sur la vidéo (si pas en train de scroller)
    if (!this.photos || this.photos.length < 5) {
      this.takePhoto();
    }
  }

  takePhoto() {
    // Effet de flash
    this.showFlash = true;
    this.cdr.detectChanges();

    // Prendre la photo
    this.camera.takePhoto();

    // Cacher le flash après 200ms
    setTimeout(() => {
      this.showFlash = false;
      this.cdr.detectChanges();
    }, 200);
  }

  async onNameSubmitted(event: any) {
    const name = event.name;
    const photo = event.photo;

    this.createdName = name;
    this.identificationStage = IdentificationStage.WAIT_MAINTENANCE_SHEET;
    this.cdr.markForCheck();

    // Compress the photo before sending (max 800px width, 85% quality)
    const compressedPhoto = await this.compressImage(photo, 800, 0.85);

    const toSend = {
      scientific_name: _.get(this.selected, "scientificName"),
      common_name: _.get(this.selected, "commonNames[0]"),
      identification_source: "PlantNet",
      gbif_id: Number(_.get(this.selected, "gbif")),
      name: this.createdName,
      photo_base64: compressedPhoto
    }

    this.maintenanceSheetService.createMaintenanceSheet(toSend).subscribe({
      next: (res) => {
        this.newMaintenanceSheet = res;
        this.cdr.detectChanges();
        this.goNextStep();
      },
      error: (err) => {
        // @TODO (PLM) mettre gestion des erreurs
        this.identificationStage = IdentificationStage.GIVE_A_NAME;
        this.cdr.detectChanges();
        console.error('Erreur création de fiche', err)
      }
    });
  }

  choseResult(index: number) {
    if (this.suggestions) {
      this.selected = this.suggestions[index]
      this.identificationStage = IdentificationStage.SUGGESTION_CHOSEN;
      this.cdr.markForCheck();
    } else {
      console.log("no results");
    }
  }

  submitPictures() {
    if (this.photos.length === 0) {
      console.warn("Aucune photo disponible");
      return;
    }
    const blobs: Blob[] = this.photos.map((photoDataUrl) => this.dataURLtoBlob(photoDataUrl));

    this.identificationStage = IdentificationStage.WAIT_SUGGESTIONS;
    this.cdr.markForCheck();


    this.maintenanceSheetService.identifyPlantFromBlobs(blobs).subscribe({
      next: (res) => {
        console.log("Résultat identification:", res);

        this.suggestions = _.get(res, "results", []).map((item: any) => {
          return {
            commonNames: _.get(item, "species.commonNames", []),
            scientificNameWithoutAuthor: _.get(item, "species.scientificNameWithoutAuthor"),
            scientificName: _.get(item, "species.scientificName"),
            gbif: _.get(item, "gbif.id"),
            score: _.get(item, "score"),
            images: _.get(item, "images", []).map((img: any) => {
              return {
                timestamp: _.get(img, "date.timestamp"),
                organ: _.get(img, "organ"),
                url: _.get(img, "url.m")
              }
            })
          }
        });
        this.selected = null;
        this.identificationStage = IdentificationStage.DISPLAY_SUGGESTIONS;
        this.cdr.markForCheck();
        this.goNextStep();
      },
      error: (err) => console.error("Erreur:", err)
    });
  }

  private dataURLtoBlob(dataURL: string): Blob {
    const byteString = atob(dataURL.split(',')[1]);
    const mimeString = dataURL.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    return new Blob([ab], {type: mimeString});
  }

  /**
   * Compress an image to reduce file size
   * @param dataUrl - Base64 data URL of the image
   * @param maxWidth - Maximum width in pixels (default: 800)
   * @param quality - JPEG quality from 0 to 1 (default: 0.85)
   * @returns Compressed image as base64 data URL
   */
  private compressImage(dataUrl: string, maxWidth: number = 800, quality: number = 0.85): Promise<string> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        const canvas = document.createElement('canvas');
        let width = img.width;
        let height = img.height;

        // Calculate new dimensions maintaining aspect ratio
        if (width > maxWidth) {
          height = (height * maxWidth) / width;
          width = maxWidth;
        }

        canvas.width = width;
        canvas.height = height;

        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('Could not get canvas context'));
          return;
        }

        // Draw and compress
        ctx.drawImage(img, 0, 0, width, height);
        const compressedDataUrl = canvas.toDataURL('image/jpeg', quality);

        console.log(`Image compressed: ${(dataUrl.length / 1024).toFixed(1)}KB → ${(compressedDataUrl.length / 1024).toFixed(1)}KB`);
        resolve(compressedDataUrl);
      };
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = dataUrl;
    });
  }

  protected readonly IdentificationStage = IdentificationStage;
  protected readonly StepIndex = StepIndex;
}
