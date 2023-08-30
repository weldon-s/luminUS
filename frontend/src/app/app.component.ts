import { Component, OnInit } from '@angular/core';
import { KeyValuePipe } from '@angular/common';
import { ApiService } from './api.service';

interface Device {
  alias: string;
  type: string;
  connected: boolean;
}

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass']
})
export class AppComponent implements OnInit {
  BULB_TYPE = "IOT.SMARTBULB";

  devices: { [key: string]: Device };

  constructor(private apiService: ApiService) {
    this.devices = {};
  }

  ngOnInit(): void {
    this.apiService.request("get_all").subscribe((data) => {
      this.devices = data;
    });
  }

  connect(ip: string): void {
    this.apiService.request(`${ip}/new`).subscribe((data) => {
      if (data.success) {
        this.devices[ip].connected = true;
      }
      else {
        alert(`Failed to connect to ${this.devices[ip].alias}`);
      }
    });
  }

  on(ip: string): void {
    this.apiService.request(`${ip}/on`).subscribe((data) => {
      if (data.success) { }
      else {
        alert(`Failed to turn on ${this.devices[ip].alias}`);
      }
    });
  }

  off(ip: string): void {
    this.apiService.request(`${ip}/off`).subscribe((data) => {
      if (data.success) { }
      else {
        alert(`Failed to turn off ${this.devices[ip].alias}`);
      }
    });
  }
}
