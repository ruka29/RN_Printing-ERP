import {Component, inject} from '@angular/core';
import {NavigationEnd, Router, RouterOutlet} from '@angular/router';
import {ProfileViewComponent} from "./profile-view/profile-view.component";
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { OnInit } from '@angular/core';
import {NgClass} from '@angular/common';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ProfileViewComponent, NgClass],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent implements OnInit {
  title = 'frontend';
  isLoginPage = false;
  showProfile: boolean = false;
  protected user?: {
    employee_id: any;
    first_name: any;
    last_name: any;
    email: any;
    department_id: any;
    user_role: any;
  };
  activeTab: string = 'dashboard';

  constructor(private router: Router, private http: HttpClient) {
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.isLoginPage = event.url.includes('/login');
      }
    });
  }

  ngOnInit() {
    this.getUser();
  }

  getCookie(name: string): string | null {
    const match = document.cookie.match(
      new RegExp('(^| )' + name + '=([^;]+)')
    );
    return match ? decodeURIComponent(match[2]) : null;
  }

  getUser() {
    const url = `https://hgzvgwmn-8000.asse.devtunnels.ms/api/employees/get-user`; // endpoint for single user
    const token = this.getCookie('jwt_token');

    if (!token) {
      console.error('JWT token not found');
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`,
    });

    this.http.get<{ user: any }>(url, { headers }).subscribe({
      next: (response) => {
        console.log('User fetched successfully:', response.user);
        this.user = {
          employee_id: response?.user?.employee_id,
          first_name: response?.user?.first_name,
          last_name: response?.user?.last_name,
          email: response?.user?.email,
          department_id: response?.user?.department_id,
          user_role: response?.user?.user_role,
        };
      },
      error: (error) => {
        console.error('Error fetching user:', error);
      },
    });
  }

  viewDetails() {
    this.showProfile = true;
  }

  closeProfile() {
    this.showProfile = false;
  }

  setActiveTab(tab: string) {
    this.activeTab = tab;

    // switch (tab) {
    //   case 'dashboard':
    //     this.router.navigate(['/dashboard']);
    //     break;
    //   case 'manage-sales-order':
    //     this.router.navigate(['/poe']);
    //     break;
    //   case 'new-sales-order':
    //     this.router.navigate(['/pov']);
    //     break;
    //   case 'manage-employees':
    //     this.router.navigate(['/']);
    //     break;
    //   default:
    //     console.warn(`No route configured for tab: ${tab}`);
    // }
  }

  onLogout() {
    sessionStorage.removeItem('user');
    document.cookie =
      'jwt_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    this.router.navigate(['/login']);
  }
}
