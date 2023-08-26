import { Component, OnInit } from '@angular/core';
import { KeyValuePipe } from '@angular/common';
import { ApiService } from './api.service';

interface Device {
  alias: string;
  type: string;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass']
})
export class AppComponent implements OnInit {
  title = 'luminUS';
  devices: { [key: string]: Device };

  constructor(private apiService: ApiService) {
    this.devices = {};
  }

  ngOnInit(): void {
    this.apiService.getDevices().subscribe((data) => {
      this.devices = data;
    });
  }
}
