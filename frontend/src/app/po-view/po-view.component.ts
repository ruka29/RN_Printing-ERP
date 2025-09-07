import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { PoEnterComponent } from "../po-enter/po-enter.component";

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
  imports: [CommonModule, FormsModule, PoEnterComponent],
  templateUrl: './po-view.component.html',
  styleUrl: './po-view.component.scss'
})
export class PoViewComponent {
  showForm: boolean = false;

  // This variable will hold the data of the item being viewed/edited
  viewData: viewI | null = null;

  // Use a single data array for the table
  item = [
    { id: 1, customer: 'JK HOLDINGS (PVT) LTD.', salseOderNo: 'S000526', POdate: '30/08/2025 12:35', poValue: '370,000', estimatedDate: '07/09/2025', status: 'Approved' },
    { id: 1, customer: 'PRINTING WORLD', salseOderNo: 'S000513', POdate: '26/08/2025 14:26', poValue: '1,500,000', estimatedDate: '06/09/2025', status: 'Completed' },
    { id: 1, customer: 'LUMALA MOTORS', salseOderNo: 'S000506', POdate: '26/08/2025 16:09', poValue: '50,000', estimatedDate: 'Order Canceled', status: 'Rejected' },
  ];

  getRowClasses(status: string): string {
    switch (status) {
      case 'Pending':
        return 'bg-blue-100 text-green-800 p-1 rounded-md';
      case 'Completed':
        return 'bg-green-100 text-green-800 p-1 rounded-md';
      case 'Rejected':
        return 'bg-red-100 text-red-800 p-1 px-3 rounded-md';
      case 'Approved':
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
