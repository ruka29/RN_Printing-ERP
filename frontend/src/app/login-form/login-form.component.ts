import { NgIf } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component, inject } from '@angular/core';
import {
  FormControl,
  FormGroup,
  ReactiveFormsModule,
  Validators,
} from '@angular/forms';
import { Router } from '@angular/router';

@Component({
  selector: 'app-login-form',
  standalone: true,
  imports: [ReactiveFormsModule, NgIf],
  templateUrl: './login-form.component.html',
  styleUrl: './login-form.component.scss',
})
export class LoginFormComponent {
  // private http = inject(HttpClient);
  private router = inject(Router);
  errormessage: string = '';

  loginForm = new FormGroup({
    email: new FormControl('', [Validators.required, Validators.minLength(3)]),
    password: new FormControl('', [Validators.required]),
  });

  onSubmit() {
    // if (this.loginForm.valid) {
    //   const url = 'http://localhost:8080/api/auth/login';
    //   const loginData = this.loginForm.value;

    //   this.http.post<{ jwt_token: string }>(url, loginData).subscribe({
    //     next: (response) => {
    //       console.log('Login Successful:', response);

    //       const jwt_token = response.jwt_token;
    //       const expiration = new Date();
    //       expiration.setTime(expiration.getTime() + 60 * 60 * 1000);
    //       document.cookie = `jwt_token = ${jwt_token}; expires=${expiration.toUTCString()}; path=/`;

    //       this.router.navigate(['/dashboard']);
    //     },
    //     error: (error) => {
    //       if (error.error && error.error.error) {
    //         console.error('Login Failed:', error.error.error);
    //         this.errormessage = error.error.error;
    //       } else {
    //         console.error('Login Failed:', 'An unknown error occurred.');
    //         this.errormessage = 'An unknown error occurred.';
    //       }
    //     },
    //   });
    // } else {
    //   console.log('Invalid Form');
    //   this.errormessage = 'Please enter valid credentials!';
    // }
  }
}
