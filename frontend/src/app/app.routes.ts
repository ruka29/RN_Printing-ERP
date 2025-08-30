import { Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { PoEnterComponent } from './po-enter/po-enter.component';
import { PoViewComponent } from './po-view/po-view.component';

export const routes: Routes = [
    {path: '', component: LoginComponent,},
    {path: 'dashboard', component: DashboardComponent,},
    {path: 'poe', component: PoEnterComponent,},
    {path: 'pov', component: PoViewComponent,},
];
