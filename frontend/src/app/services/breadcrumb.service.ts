import { Injectable, signal, inject } from '@angular/core';
import { Router, NavigationEnd } from '@angular/router';
import { filter } from 'rxjs/operators';
import { BreadcrumbItem } from '../components/breadcrumbs/component';

@Injectable({
  providedIn: 'root'
})
export class BreadcrumbService {
  private router = inject(Router);
  private itemsSignal = signal<BreadcrumbItem[]>([]);
  
  // Expose as readonly signal
  items = this.itemsSignal.asReadonly();

  constructor() {
    // Clear breadcrumbs on every navigation
    this.router.events
      .pipe(filter(event => event instanceof NavigationEnd))
      .subscribe(() => {
        this.clear();
      });
  }

  /**
   * Set the breadcrumb items
   */
  setItems(items: BreadcrumbItem[]): void {
    this.itemsSignal.set(items);
  }

  /**
   * Clear all breadcrumb items
   */
  clear(): void {
    this.itemsSignal.set([]);
  }

  /**
   * Add a single item to the end
   */
  addItem(item: BreadcrumbItem): void {
    this.itemsSignal.update(current => [...current, item]);
  }

  /**
   * Remove the last item
   */
  removeLastItem(): void {
    this.itemsSignal.update(current => current.slice(0, -1));
  }
}
