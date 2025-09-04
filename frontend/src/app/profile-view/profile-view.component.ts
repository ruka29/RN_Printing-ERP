import { Component, EventEmitter, Output } from '@angular/core';

@Component({
  selector: 'app-profile-view',
  imports: [],
  templateUrl: './profile-view.component.html',
  styleUrl: './profile-view.component.scss'
})
export class ProfileViewComponent {
 @Output() close = new EventEmitter<void>();

  closePopup() {
    this.close.emit(); 
  }
}
