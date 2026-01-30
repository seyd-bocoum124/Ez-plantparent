import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import type { Observable } from 'rxjs';
import {AuthService, User} from '../../services/auth/auth.service';

@Component({
  selector: 'app-landing',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './landing.html',
  styleUrls: ['./landing.scss']
})
export class LandingComponent {
  user$: Observable<User>;
  constructor(public auth: AuthService) { this.user$ = this.auth.user$; }
}
