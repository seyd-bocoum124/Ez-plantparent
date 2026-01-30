import { Component } from '@angular/core';
import {Router, RouterLink} from '@angular/router';
import {AsyncPipe} from '@angular/common';
import type {Observable} from 'rxjs';
import {MatIconButton} from '@angular/material/button';
import {MatToolbar} from '@angular/material/toolbar';
import {GoogleSigninComponent} from '../google-signin/google-signin.component';
import {AuthService, User} from '../../services/auth/auth.service';
import {MatIcon} from '@angular/material/icon';
import {MatMenu, MatMenuItem, MatMenuTrigger} from '@angular/material/menu';
import {BreadcrumbComponent} from "../breadcrumbs/component";
import {BreadcrumbService} from '../../services/breadcrumb.service';

@Component({
  selector: 'main-menu',
    imports: [
        RouterLink,
        AsyncPipe,
        GoogleSigninComponent,
        MatToolbar,
        MatIcon,
        MatMenu,
        MatMenuTrigger,
        MatIconButton,
        MatMenuItem,
        BreadcrumbComponent,
    ],
  templateUrl: './menu.html',
  styleUrl: './menu.scss'
})
export class Menu {
  user$: Observable<User>;

  constructor(
    public auth: AuthService,
    private router: Router,
    private breadcrumbService: BreadcrumbService
) {
    this.user$ = this.auth.user$;
  }

  get items() {
    return this.breadcrumbService.items();
  }
  async logout() {
    try {
      await this.auth.logout();
    } catch {
    } finally {
      this.router.navigateByUrl('/');
    }
  }
}
