import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private serverUrl: string = 'http://localhost:5000';

  constructor(private http: HttpClient) { }

  request(url: string): Observable<any> {
    return this.http.get(`${this.serverUrl}/${url}`);
  }
}