import { Component, Input, computed, signal } from '@angular/core';
import { RouterModule } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { CommonModule } from '@angular/common';
import {MatToolbar} from '@angular/material/toolbar';
import {MatButton, MatIconButton} from '@angular/material/button';
import {MatMenu, MatMenuItem, MatMenuTrigger} from '@angular/material/menu';
import {NativeService} from '../../services/native.service';

export interface BreadcrumbItem {
  label: string;
  routerLink?: any[];
  queryParams?: { [key: string]: any };
  childs?: BreadcrumbItem[];
}

@Component({
  selector: 'app-breadcrumb',
  standalone: true,
  imports: [CommonModule, RouterModule, MatIconModule, MatToolbar, MatButton, MatIconButton, MatMenu, MatMenuItem, MatMenuTrigger],
  templateUrl: './component.html',
  styleUrls: ['./component.scss']
})
export class BreadcrumbComponent {
  @Input() set items(value: BreadcrumbItem[]) {
    this.itemsSignal.set(value);
  }
  constructor(private nativeService: NativeService) {
    this.isNativePlatform = this.nativeService.isNative();
    if(this.isNativePlatform) {
      this.itemLimit = 2
    }
  }

  isNativePlatform: boolean;

  private itemLimit = 8;

  private itemsSignal = signal<BreadcrumbItem[]>([]);

  // Computed: items cachés (tous sauf les 3 derniers si > 3)
  hiddenItems = computed(() => {
    const items = this.itemsSignal();
    return items.length > this.itemLimit ? items.slice(0, -this.itemLimit) : [];
  });

  // Computed: items visibles (les 3 derniers si > 3, sinon tous)
  visibleItems = computed(() => {
    const items = this.itemsSignal();
    return items.length > this.itemLimit ? items.slice(-this.itemLimit) : items;
  });

  // Computed: indique s'il y a des items cachés
  hasHiddenItems = computed(() => this.hiddenItems().length > 0);
  
  // Computed: dernier item caché (pour vérifier s'il a des enfants)
  lastHiddenItem = computed(() => {
    const hidden = this.hiddenItems();
    return hidden.length > 0 ? hidden[hidden.length - 1] : null;
  });
}


