import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-manage-employee',
  imports: [CommonModule,FormsModule],
  templateUrl: './manage-employee.component.html',
  styleUrl: './manage-employee.component.scss'
})
export class ManageEmployeeComponent {
employee: any = {
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    department: '',
    role: ''
  };

  constructor() { }

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
}
