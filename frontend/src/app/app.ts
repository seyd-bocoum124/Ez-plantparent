import {Component, inject, signal} from '@angular/core';
import { RouterOutlet } from '@angular/router';
import {HttpClient} from '@angular/common/http';
import {Menu} from './components/menu/menu';
import {ErrorNotifierService} from './services/error-notifier-service';
import {AuthService} from './services/auth/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, Menu],
  templateUrl: './app.html',
  styleUrls: ['./app.scss']
})
export class App {
  protected readonly title = signal('frontend');

  private readonly auth = inject(AuthService);
  private readonly http = inject(HttpClient);

  constructor(private errorNotifier: ErrorNotifierService) {}
}
