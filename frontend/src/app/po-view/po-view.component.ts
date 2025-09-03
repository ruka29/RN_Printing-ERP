import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';

interface viewI {
  id: number;
  customer: string;
  salseOderNo: string;
  POdate: string;
  poValue: string;
  status: string;
}

@Component({
  selector: 'app-po-view',
  standalone: true, // It's better to explicitly mark it as standalone
  imports: [CommonModule, FormsModule],
  templateUrl: './po-view.component.html',
  styleUrl: './po-view.component.scss'
})
export class PoViewComponent {
  showForm: boolean = false;

  // This variable will hold the data of the item being viewed/edited
  viewData: viewI | null = null; 

  // Use a single data array for the table
  item = [
    { id: 1, customer: 'Customer A', salseOderNo: '12345', POdate: '2023-01-01', poValue: '$6,456.80', status: 'Completed' },
    { id: 2, customer: 'Customer B', salseOderNo: '12346', POdate: '2023-01-02', poValue: '$7,123.40', status: 'Processing' },
    { id: 3, customer: 'Customer C', salseOderNo: '12347', POdate: '2023-01-03', poValue: '$8,901.20', status: 'Rejected' },
  ];

  getRowClasses(status: string): string {
    switch (status) {
      case 'Completed':
        return 'bg-green-100 text-green-800 p-1 rounded-md';
      case 'Rejected':
        return 'bg-red-100 text-red-800 p-1 px-3 rounded-md';
      case 'Processing':
        return 'bg-purple-100 text-purple-800 p-1 rounded-md';
      default:
        return '';
    }
  }

  // This method now correctly receives and stores the clicked item
  view(item: viewI) {
    this.viewData = item; // Store the clicked item's data
    this.showForm = true; // Show the form
    console.log(this.viewData); // Log the data to confirm it works
  }

  closeForm() {
    this.showForm = false;
    this.viewData = null; // Clear the data when the form is closed
  }
}