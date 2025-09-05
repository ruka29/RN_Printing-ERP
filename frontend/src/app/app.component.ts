import {Component, inject} from '@angular/core';
import {NavigationEnd, Router, RouterOutlet} from '@angular/router';
import {ProfileViewComponent} from "./profile-view/profile-view.component";
import {HttpClient, HttpHeaders} from '@angular/common/http';
import { OnInit } from '@angular/core';
import {CommonModule, NgClass} from '@angular/common';
import { NgModel } from '@angular/forms';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet,CommonModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent  {
    title = 'client';
}
