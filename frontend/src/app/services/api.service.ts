import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';

const API_BASE = 'http://localhost:5000';

export interface Image {
  id: string;
  image_id?: string; // Pour compatibilité avec les résultats de recherche
  filename: string;
  uploaded_at?: string;
  detected_objects?: any[]; // Nom utilisé par le backend
  objects_detected?: any[]; // Alias pour compatibilité
  objects_count?: number;
  object_classes?: string[];
  similarity_score?: number;
  selected?: boolean; // Pour la sélection dans la galerie
}

export interface UploadResponse {
  uploaded: Array<{ id: string; filename: string; objects_detected?: number }>;
  count: number;
  errors?: Array<{ filename: string; error: string }>;
}

export interface SearchResponse {
  query_info: any;
  results: Image[];
  count: number;
}

export interface ListResponse {
  images: Image[];
  count: number;
  total: number;
  offset: number;
  limit: number;
}

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  constructor(private http: HttpClient) {}

  /**
   * Upload une ou plusieurs images
   */
  uploadImages(files: FileList | File[]): Observable<UploadResponse> {
    const formData = new FormData();
    Array.from(files).forEach((file) => formData.append('images', file));
    return this.http.post<UploadResponse>(`${API_BASE}/upload`, formData);
  }

  /**
   * Liste toutes les images avec pagination et filtres
   */
  listImages(params?: { object_class?: string; limit?: number; offset?: number }): Observable<ListResponse> {
    let httpParams = new HttpParams();
    if (params) {
      if (params.object_class) httpParams = httpParams.set('object_class', params.object_class);
      if (params.limit) httpParams = httpParams.set('limit', params.limit.toString());
      if (params.offset) httpParams = httpParams.set('offset', params.offset.toString());
    }
    return this.http.get<ListResponse>(`${API_BASE}/images`, { params: httpParams });
  }

  /**
   * Télécharge une image par son ID
   */
  downloadImage(id: string): Observable<Blob> {
    return this.http.get(`${API_BASE}/download/${id}`, { responseType: 'blob' });
  }

  /**
   * Supprime une image
   */
  deleteImage(id: string): Observable<any> {
    return this.http.delete(`${API_BASE}/delete/${id}`);
  }

  /**
   * Recherche des images similaires
   * Mode 1: Upload d'une nouvelle image
   * Mode 2: Utilisation d'une image existante
   * Mode 3: Recherche basée sur un objet spécifique
   */
  search(payload: {
    type: 'upload' | 'existing';
    image?: File;
    image_id?: string;
    object_id?: number;
    object_class?: string;
    top_k?: number;
  }): Observable<SearchResponse> {
    const formData = new FormData();
    
    if (payload.type === 'upload' && payload.image) {
      formData.append('type', 'upload');
      formData.append('image', payload.image);
      if (payload.top_k) formData.append('top_k', payload.top_k.toString());
    } else if (payload.type === 'existing') {
      formData.append('type', 'existing');
      if (payload.image_id) formData.append('image_id', payload.image_id);
      if (payload.object_id !== undefined) formData.append('object_id', payload.object_id.toString());
      if (payload.top_k) formData.append('top_k', payload.top_k.toString());
      if (payload.object_class) formData.append('object_class', payload.object_class);
    }
    
    return this.http.post<SearchResponse>(`${API_BASE}/search`, formData);
  }

  /**
   * Applique une transformation à une image
   */
  transform(id: string, transform: string, params: any): Observable<any> {
    return this.http.post(`${API_BASE}/transform/${id}`, {
      transform,
      params
    });
  }

  /**
   * Vérifie que l'API est accessible
   */
  healthCheck(): Observable<{ status: string }> {
    return this.http.get<{ status: string }>(`${API_BASE}/health`);
  }

  /**
   * Récupère les images avec pagination et filtres
   */
  getImages(page: number, pageSize: number, objectClassFilter: string): Observable<{ images: Image[], total: number }> {
    let params = new HttpParams()
      .set('offset', ((page - 1) * pageSize).toString())
      .set('limit', pageSize.toString());
    if (objectClassFilter) {
      params = params.set('object_class', objectClassFilter);
    }
    return this.http.get<any>(`${API_BASE}/images`, { params });
  }

  /**
   * Récupère les descripteurs détaillés d'une image ou d'un objet
   * @param imageId ID de l'image
   * @param objectId (optionnel) index de l'objet
   */
  getDescriptors(imageId: number | string, objectId?: number): Observable<any> {
    let url = `${API_BASE}/descriptors/${imageId}`;
    if (objectId !== undefined) {
      url += `/${objectId}`;
    }
    return this.http.get<any>(url);
  }
}
