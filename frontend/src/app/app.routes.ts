import {Routes} from '@angular/router';
import {DashboardComponent} from './dashboard/dashboard.component';
import {PoEnterComponent} from './po-enter/po-enter.component';
import {PoViewComponent} from './po-view/po-view.component';
import {LoginComponent} from './login/login.component';
import {authGuard} from './auth.guard';
import { ManageEmployeeComponent } from './manage-employee/manage-employee.component';

export const routes: Routes = [
  {path: 'login', component: LoginComponent,},
  {path: 'dashboard', component: DashboardComponent, canActivate: [authGuard]},
  {path: 'poe', component: PoEnterComponent,},
  {path: 'pov', component: PoViewComponent,},
  {path: 'employee', component: ManageEmployeeComponent,},
  {path: '**', redirectTo: '/dashboard'}
];
