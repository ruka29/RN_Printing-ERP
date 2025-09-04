import { Component } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { ProfileViewComponent } from "./profile-view/profile-view.component";

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ProfileViewComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'frontend';
  isLoginPage = false;
  constructor(private router: Router) {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.isLoginPage = event.url.includes('/login');
      }
    });
  }
 showProfile: boolean = false; 

  viewDetails() {
    this.showProfile = true;
  }

  closeProfile() {
    this.showProfile = false;
  }
}
