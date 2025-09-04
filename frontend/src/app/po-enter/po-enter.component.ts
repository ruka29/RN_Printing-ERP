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
        { id: 1, itemName: 'Create report', unitPrice: '$12' ,quantity:"50" ,total:"$6,4568"},
        { id: 2, itemName: 'Review proposal', unitPrice: '$15', quantity:"50" ,total:"$6,4568"},
        { id: 3, itemName: 'Sign contract', unitPrice: '$14',quantity:"50" ,total:"$6,4568" },
        { id: 5, itemName: 'Check inventory', unitPrice: '$15',quantity:"50" ,total:"$6,4568" },
        { id: 6, itemName: 'Finalize budget', unitPrice: '$10',quantity:"50" ,total:"$6,4568" }
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
    poNumber: '',
    customer: '',
    currency: '',
    tValue: '',
    inAddress: '',
    deliAddress: ''
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
}
