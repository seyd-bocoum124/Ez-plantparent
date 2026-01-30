import { Component, ElementRef, ViewChild, AfterViewInit, Output, EventEmitter, OnDestroy } from '@angular/core';
import {NativeService} from '../../services/native.service';

@Component({
  selector: 'app-camera',
  templateUrl: './component.html',
  styleUrls: ['./component.scss']
})
export class CameraComponent implements AfterViewInit, OnDestroy {
  @ViewChild('video') videoRef!: ElementRef<HTMLVideoElement>;

  @Output() photosChange = new EventEmitter<string[]>();
  @Output() videoTap = new EventEmitter<void>(); // Émet quand on tap sur la vidéo
  private photos: string[] = [];
  private stream?: MediaStream;
  isNativePlatform: boolean;

  // Pour détecter tap vs scroll
  private touchStartX = 0;
  private touchStartY = 0;
  private touchStartTime = 0;

  constructor(private nativeService: NativeService) {
    this.isNativePlatform = this.nativeService.isNative();
  }

  async ngAfterViewInit() {
    // Essayer getUserMedia sur web ET mobile (fonctionne dans Capacitor WebView)
    try {
      console.log('[Camera] Requesting getUserMedia...');
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: {
          facingMode: 'environment', // Caméra arrière
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      });

      if (this.videoRef?.nativeElement) {
        this.videoRef.nativeElement.srcObject = this.stream;
        console.log('[Camera] Video stream set successfully');
      }
    } catch (error) {
      console.error('[Camera] getUserMedia error:', error);
      alert('Erreur caméra: ' + JSON.stringify(error));
    }
  }

  async takePhoto() {
    // Utiliser canvas avec getUserMedia (fonctionne web ET mobile)
    try {
      const video = this.videoRef.nativeElement;
      if (!video || video.readyState !== video.HAVE_ENOUGH_DATA) {
        console.error('[Camera] Video not ready');
        alert('La vidéo n\'est pas prête');
        return;
      }

      const canvas = document.createElement('canvas');
      const context = canvas.getContext('2d');
      if (context) {
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        const imageData = canvas.toDataURL('image/jpeg', 0.9);
        this.photos.push(imageData);
        this.photosChange.emit(this.photos);
        console.log('[Camera] Photo captured, total:', this.photos.length);
      }
    } catch (error) {
      console.error('[Camera] Error taking photo:', error);
      alert('Erreur capture: ' + JSON.stringify(error));
    }
  }

  onTouchStart(event: TouchEvent) {
    this.touchStartX = event.touches[0].clientX;
    this.touchStartY = event.touches[0].clientY;
    this.touchStartTime = Date.now();
  }

  onTouchEnd(event: TouchEvent) {
    const touchEndX = event.changedTouches[0].clientX;
    const touchEndY = event.changedTouches[0].clientY;
    const touchEndTime = Date.now();

    // Calculer la distance et le temps
    const deltaX = Math.abs(touchEndX - this.touchStartX);
    const deltaY = Math.abs(touchEndY - this.touchStartY);
    const deltaTime = touchEndTime - this.touchStartTime;

    // Si mouvement < 10px et durée < 300ms = c'est un tap
    if (deltaX < 10 && deltaY < 10 && deltaTime < 300) {
      console.log('[Camera] Video tapped!');
      this.videoTap.emit();
    }
  }

  ngOnDestroy() {
    if (this.stream) {
      this.stream.getTracks().forEach(track => track.stop());
    }
  }

}

