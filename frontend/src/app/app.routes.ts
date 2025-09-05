import {Routes} from '@angular/router';
import {DashboardComponent} from './dashboard/dashboard.component';
import {PoEnterComponent} from './po-enter/po-enter.component';
import {PoViewComponent} from './po-view/po-view.component';
import {LoginComponent} from './login/login.component';
import {authGuard} from './auth.guard';

export const routes: Routes = [
  {path: 'login', component: LoginComponent,},
  {path: 'dashboard', component: DashboardComponent, canActivate: [authGuard]},
  {path: 'poe', component: PoEnterComponent,},
  {path: 'pov', component: PoViewComponent,},
  {path: '**', redirectTo: '/dashboard'}
];
