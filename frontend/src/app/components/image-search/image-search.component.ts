import { Component, OnInit } from '@angular/core';
import { ApiService, Image } from '../../services/api.service';

@Component({
  selector: 'app-image-search',
  templateUrl: './image-search.component.html',
  styleUrls: ['./image-search.component.css']
})
export class ImageSearchComponent implements OnInit {
  // Mode de recherche
  searchMode: 'upload' | 'existing' = 'upload';
  
  // Upload mode
  queryFile: File | null = null;
  
  // Existing image mode
  availableImages: Image[] = [];
  selectedImageId: string = '';
  selectedObjectId: number | null = null;
  selectedImage: Image | null = null;
  
  // Résultats
  results: Image[] = [];
  loading = false;
  error: string | null = null;
  queryInfo: any = null;
  
  // Paramètres
  topK = 10;
  objectClassFilter = '';

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadAvailableImages();
  }

  loadAvailableImages() {
    this.api.listImages({ limit: 100 }).subscribe({
      next: (response) => {
        this.availableImages = response.images || [];
      },
      error: (error) => {
        console.error('Error loading images:', error);
      }
    });
  }

  onQueryFileChange(event: any) {
    const files = event.target.files;
    if (files && files.length > 0) {
      this.queryFile = files[0];
    }
  }

  onImageSelect(imageId: string) {
    this.selectedImageId = imageId;
    this.selectedImage = this.availableImages.find(img => img.id === imageId) || null;
    this.selectedObjectId = null;
  }

  search() {
    this.loading = true;
    this.error = null;
    this.results = [];
    this.queryInfo = null;

    const payload: any = {
      top_k: this.topK
    };

    if (this.searchMode === 'upload') {
      if (!this.queryFile) {
        this.error = 'Veuillez sélectionner une image à rechercher';
        this.loading = false;
        return;
      }
      payload.type = 'upload';
      payload.image = this.queryFile;
    } else {
      if (!this.selectedImageId) {
        this.error = 'Veuillez sélectionner une image existante';
        this.loading = false;
        return;
      }
      payload.type = 'existing';
      payload.image_id = this.selectedImageId;
      if (this.selectedObjectId !== null) {
        payload.object_id = this.selectedObjectId;
      }
    }

    if (this.objectClassFilter) {
      payload.object_class = this.objectClassFilter;
    }

    this.api.search(payload).subscribe({
      next: (response) => {
        this.results = response.results || [];
        this.queryInfo = response.query_info;
        this.loading = false;
      },
      error: (error) => {
        this.error = `Erreur lors de la recherche: ${error.error?.error || error.message}`;
        this.loading = false;
        console.error('Search error:', error);
      }
    });
  }

  viewImage(image: Image) {
    window.open(`http://localhost:5000/download/${image.id}`, '_blank');
  }

  getObjectClasses(): string[] {
    if (!this.selectedImage || !this.selectedImage.objects_detected) {
      return [];
    }
    return Array.from(new Set(
      this.selectedImage.objects_detected.map(obj => obj.class)
    ));
  }
}
