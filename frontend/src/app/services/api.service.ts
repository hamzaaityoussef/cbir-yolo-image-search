import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

const API_BASE = 'http://localhost:5000';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor(private http: HttpClient) {}

  uploadImages(files: FileList | File[]): Observable<any> {
    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append('images', file));
    return this.http.post(`${API_BASE}/upload`, formData);
  }

  listImages(): Observable<any> {
    // TODO: endpoint à exposer si besoin pour lister
    return this.http.get(`${API_BASE}/search`);
  }

  downloadImage(id: string): Observable<Blob> {
    return this.http.get(`${API_BASE}/download/${id}`, { responseType: 'blob' });
  }

  deleteImage(id: string): Observable<any> {
    return this.http.delete(`${API_BASE}/delete/${id}`);
  }

  search(payload: any): Observable<any> {
    return this.http.post(`${API_BASE}/search`, payload);
  }

  transform(id: string, payload: any): Observable<any> {
    return this.http.post(`${API_BASE}/transform/${id}`, payload);
  }
}

