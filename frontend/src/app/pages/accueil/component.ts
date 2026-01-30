import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import type { Observable } from 'rxjs';
import {AuthService, User} from '../../services/auth/auth.service';
import {MatButton} from '@angular/material/button';
import {RouterLink} from '@angular/router';
import {BreadcrumbService} from '../../services/breadcrumb.service';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule, MatButton, RouterLink],
  templateUrl: './component.html',
  styleUrls: ['./component.scss']
})
export class AccueilComponent {
  user$: Observable<User>;
  constructor(public auth: AuthService, private breadcrumbService: BreadcrumbService) { this.user$ = this.auth.user$; }

  async ngOnInit() {
    this.breadcrumbService.setItems([
      { label: 'Accueil', routerLink: ['/accueil'],
        childs: [
          {label: 'Maintenance', routerLink: ['/maintenance-schedule']},
          {label: 'Plantes', routerLink: ['/my-plants']},
        ]
      },
    ]);
  }
}
