import { Component, OnInit } from '@angular/core';
import {FormsModule} from '@angular/forms';

@Component({
  selector: 'app-dashboard',
  templateUrl: './dashboard.component.html',
  imports: [
    FormsModule
  ],
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  // KPI Data
  totalPoProcessed: string = 'XXXX';
  totalApprovedPo: string = 'XXXX';
  todayTotalIntake: string = 'XXXX';

  // Progress Bar Data
  progressData = [
    { label: 'Current Period', value: '2,450', progress: 82, color: 'bg-blue-500' },
    { label: 'Previous Period', value: '2,180', progress: 73, color: 'bg-green-500' },
    { label: 'Target Achievement', value: '3,000', progress: 92, color: 'bg-purple-500' }
  ];

  // Chart options
  selectedTimeRange: string = 'month';
  timeRangeOptions = [
    { value: 'month', label: 'Last Month' },
    { value: 'week', label: 'Last Week' },
    { value: 'day', label: 'Today' }
  ];

  constructor() { }

  ngOnInit(): void {
    this.loadDashboardData();
  }

  private loadDashboardData(): void {
    // Simulate API call
    setTimeout(() => {
      this.totalPoProcessed = '2,450';
      this.totalApprovedPo = '2,180';
      this.todayTotalIntake = '125';
    }, 500);
  }

  onTimeRangeChange(event: any): void {
    this.selectedTimeRange = event.target.value;
    console.log('Time range changed:', this.selectedTimeRange);
    // Implement chart update logic here
  }

  refreshData(): void {
    this.loadDashboardData();
  }
}
