import {ChangeDetectorRef, Component, EventEmitter, Output, ViewChild} from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule, FormGroup, FormControl, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import {CameraComponent} from '../../../../components/camera/component';
import {MatIcon} from '@angular/material/icon';
import {DomSanitizer, SafeUrl} from '@angular/platform-browser';

@Component({
  selector: 'app-plant-naming-form',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    CameraComponent,
    MatIcon,
  ],
  templateUrl: './component.html',
  styleUrls: ['./component.scss']
})
export class PlantNamingFormComponent {
  @Output() submitForm = new EventEmitter<any>();
  @ViewChild(CameraComponent) camera!: CameraComponent;

  photos: string[] = [];
  showFlash = false;

  form = new FormGroup({
    name: new FormControl<string>('', [Validators.required, Validators.maxLength(50)])
  });

  constructor(
    private cdr: ChangeDetectorRef,
    private sanitizer: DomSanitizer
  ) {}


  onSubmit() {
    if (this.form.valid) {
      console.log({
        name: this.form.value.name,
        photos: this.photos,
      })
      // this.submitForm.emit(this.form.value.name as string);
      this.submitForm.emit({
        name: this.form.value.name,
        photo: this.photos[0],
      });
    }
  }


  onPhotosUpdate(updated: string[]) {
    this.photos = updated;
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

  getSafeUrl(url: string): SafeUrl {
    return this.sanitizer.bypassSecurityTrustUrl(url);
  }

  removePhoto(index: number) {
    this.photos.splice(index, 1);
  }
}
