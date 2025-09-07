import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FormsModule, ɵInternalFormsSharedModule } from "@angular/forms";
interface Item {
  id: number;
  itemName: string;
  unitPrice: string;
  quantity: string;
  total: string;
}
@Component({
  selector: 'app-po-enter',
  imports: [ɵInternalFormsSharedModule,CommonModule,FormsModule],
  templateUrl: './po-enter.component.html',
  styleUrl: './po-enter.component.scss'
})
export class PoEnterComponent {

  data = [
    { id: 1, itemName: '90MM x 40MM BLANK STICKER', unitPrice: '0.20' ,quantity:"100000" ,total:"20,000"},
    { id: 2, itemName: '500g LOOSE TEA', unitPrice: '7.00', quantity:"50000" ,total:"350,000"}
  ];
  isEditable: boolean = false;
  selectedItem: Item | null = null;
  itemName:string='';
  id:any;
  toggleEditMode() {
    this.isEditable = !this.isEditable;
  }
  //====save data======
  saveData = {
    poNumber: 'PO-LC-16540',
    customer: 'JK HOLDINGS (PVT) LTD.',
    currency: 'LKR',
    tValue: '370,000',
    inAddress: 'JK HOLDINGS (PVT) LTD., PARK ROAD, AUTHURUGIRIYA.',
    deliAddress: 'JK HOLDINGS (PVT) LTD., PARK ROAD, AUTHURUGIRIYA.'
  };
  save(){
    console.log(this.saveData);
    this.saveData = {
      poNumber: '',
      customer: '',
      currency: '',
      tValue: '',
      inAddress: '',
      deliAddress: ''
    };
  }
  showForm: boolean = false;

  openForm(item: Item) {
    this.selectedItem = item;
    this.showForm = true;
  }

  closeForm() {
    this.showForm = false;
  }
  saveChanges(){
    if (this.selectedItem) {
      console.log('Pop-up form data:', this.selectedItem);
      this.closeForm();
    }
  }
  showExtractedData: boolean = false;
  extractAndDisplayData() {

    this.showExtractedData = true;
  }
}
