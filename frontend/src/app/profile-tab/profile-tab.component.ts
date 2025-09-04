import { CommonModule } from '@angular/common';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { NotificationComponent } from '../notification/notification.component';
import { NotificationService } from '../notification.service';

@Component({
  selector: 'app-profile-tab',
  standalone: true,
  imports: [CommonModule, ReactiveFormsModule, NotificationComponent],
  templateUrl: './profile-tab.component.html',
  styleUrl: './profile-tab.component.scss',
})
export class ProfileTabComponent {
  private http = inject(HttpClient);
  message: string = '';
  messageType: string = '';

  name: string = '';
  email: string = '';
  mobile: string = '';
  address: string = '';
  role: string = '';

  isEditing: boolean = false;

  selectedImage: File | null = null;

  userForm = new FormGroup({
    id: new FormControl('', [Validators.required]),
    name: new FormControl('', [Validators.required]),
    email: new FormControl('', [Validators.required, Validators.email]),
    mobile: new FormControl('', [Validators.required]),
    address: new FormControl('', [Validators.required]),
    role: new FormControl('', [Validators.required]),
  });

  constructor(private notificationService: NotificationService) {
    const user = sessionStorage.getItem('user');
    if (user) {
      const userData = JSON.parse(user);
      this.name = userData.name;
      this.email = userData.email;
      this.userForm.patchValue({
        id: userData.id,
        name: userData.name,
        email: userData.email,
        mobile: userData.mobile,
        address: userData.address,
        role: userData.role,
      });
    }
  }

  getCookie(name: string): string | null {
    const match = document.cookie.match(
      new RegExp('(^| )' + name + '=([^;]+)')
    );
    return match ? decodeURIComponent(match[2]) : null;
  }

  setIsEditing() {
    this.isEditing = !this.isEditing;
  }

  onFileSelected(event: Event): void {
    const fileInput = event.target as HTMLInputElement;

    if (fileInput.files && fileInput.files.length > 0) {
      this.selectedImage = fileInput.files[0];
      console.log('Selected image:', this.selectedImage);
    }
  }

  onSubmit() {
    if (this.userForm.valid) {
      const url = 'http://localhost:8080/api/manage-users/update-profile';
      const userData = this.userForm.value;

      console.log('User Data:', userData);
      const token = this.getCookie('jwt_token');

      const formData = new FormData();

      Object.entries(this.userForm.value).forEach(([key, value]) => {
        formData.append(key, value as string);
      });

      if (this.selectedImage) {
        formData.append('image', this.selectedImage);
      }

      if (token) {
        const headers = new HttpHeaders({
          Authorization: `Bearer ${token}`,
        });

        this.http
          .post<{ message: string; error: any }>(url, formData, { headers })
          .subscribe({
            next: (response) => {
              console.log('Success:', response);

              this.isEditing = !this.isEditing;

              this.message = response.message;
              this.messageType = 'success';

              setTimeout(() => {
                this.message = '';
                this.messageType = '';
              }, 5000);
            },
            error: (error) => {
              if (error.error && error.error.error) {
                console.error('User update failed:', error.error.error);
                this.message = error.error.error;
                this.messageType = 'error';

                setTimeout(() => {
                  this.message = '';
                  this.messageType = '';
                }, 5000);
              } else {
                console.error('update failed:', 'An unknown error occurred.');
              }
            },
          });
      }
    } else {
      console.log('Invalid Form');
      this.message = 'All fields are required!';
      this.messageType = 'error';

      setTimeout(() => {
        this.message = '';
        this.messageType = '';
      }, 5000);
    }
  }

  handleClickRequest() {
    this.notificationService.sendPasswordResetRequest(this.email);
    this.message = 'Request sent!';
    this.messageType = 'success';

    setTimeout(() => {
      this.message = '';
      this.messageType = '';
    }, 5000);
  }

  closeNotification() {
    this.message = '';
    this.messageType = '';
  }
}
