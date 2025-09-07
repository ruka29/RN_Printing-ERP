import { CommonModule } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-manage-employee',
  imports: [CommonModule, FormsModule],
  templateUrl: './manage-employee.component.html',
  styleUrl: './manage-employee.component.scss'
})
export class ManageEmployeeComponent implements OnInit {
  employee: any = {
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    department: '',
    role: ''
  };

  allEmployees: any[] = [

  ]; // store fetched users

  constructor(private http: HttpClient) { }

  ngOnInit() {
    this.getAllEmployees();
  }

  getAllEmployees() {
    const url = 'http://localhost:8000/api/employees/'; // replace with your endpoint
    const token = this.getCookie('jwt_token');

    if (!token) {
      console.error('JWT token not found');
      return;
    }

    const headers = new HttpHeaders({
      Authorization: `Bearer ${token}`
    });

    this.http.get<any[]>(url, { headers }).subscribe({
      next: (res) => {
        console.log('Fetched employees:', res);
        this.allEmployees = res;
      },
      error: (err) => console.error('Error fetching employees:', err)
    });
  }

  getCookie(name: string): string | null {
    const match = document.cookie.match(
      new RegExp('(^| )' + name + '=([^;]+)')
    );
    return match ? decodeURIComponent(match[2]) : null;
  }

  saveEmployee() {
    console.log('Employee data saved:', this.employee);
    this.resetForm();
  }

  resetForm() {
    this.employee = {
      firstName: '',
      lastName: '',
      email: '',
      password: '',
      department: '',
      role: ''
    };
  }

  cancel() {
    this.resetForm();
  }

  view(employee: any) {
    console.log('View employee:', employee);
    // Implement popup or details view
  }

  getRowClasses(status: string) {
    switch (status) {
      case 'Completed': return 'text-green-600 font-semibold';
      case 'Processing': return 'text-blue-600 font-semibold';
      case 'Rejected': return 'text-red-600 font-semibold';
      case 'Approved': return 'text-green-700 font-semibold';
      case 'Pending': return 'text-yellow-600 font-semibold';
      default: return '';
    }
  }
}
