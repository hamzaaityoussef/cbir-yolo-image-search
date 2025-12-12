import { Component, OnInit } from '@angular/core';
import { ApiService, Image } from '../../services/api.service';

@Component({
  selector: 'app-image-gallery',
  templateUrl: './image-gallery.component.html',
  styleUrls: ['./image-gallery.component.css']
})
export class ImageGalleryComponent implements OnInit {
  images: Image[] = [];
  loading = false;
  error: string | null = null;
  selectedImage: Image | null = null;
  imageUrl: string | null = null;

  // Pagination
  currentPage = 1;
  pageSize = 12;
  total = 0;

  // Filtres
  objectClassFilter = '';
  availableClasses: string[] = [];

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadImages();
  }

  loadImages() {
    this.loading = true;
    this.error = null;

    const params: any = {
      limit: this.pageSize,
      offset: (this.currentPage - 1) * this.pageSize
    };

    if (this.objectClassFilter) {
      params.object_class = this.objectClassFilter;
    }

    this.api.listImages(params).subscribe({
      next: (response) => {
        this.images = response.images || [];
        this.total = response.total || 0;
        this.loading = false;
        
        // Extraire les classes d'objets disponibles
        this.extractAvailableClasses();
      },
      error: (error) => {
        this.error = `Erreur lors du chargement: ${error.error?.error || error.message}`;
        this.loading = false;
        console.error('Load images error:', error);
      }
    });
  }

  extractAvailableClasses() {
    const classesSet = new Set<string>();
    this.images.forEach(img => {
      if (img.object_classes) {
        img.object_classes.forEach(cls => classesSet.add(cls));
      }
    });
    this.availableClasses = Array.from(classesSet).sort();
  }

  viewImage(image: Image) {
    this.selectedImage = image;
    this.api.downloadImage(image.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        this.imageUrl = url;
      },
      error: (error) => {
        console.error('Download error:', error);
        alert('Erreur lors du chargement de l\'image');
      }
    });
  }

  closeImageView() {
    this.selectedImage = null;
    if (this.imageUrl) {
      window.URL.revokeObjectURL(this.imageUrl);
      this.imageUrl = null;
    }
  }

  downloadImage(image: Image) {
    this.api.downloadImage(image.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = image.filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      },
      error: (error) => {
        console.error('Download error:', error);
        alert('Erreur lors du téléchargement');
      }
    });
  }

  deleteImage(image: Image) {
    if (!confirm(`Êtes-vous sûr de vouloir supprimer "${image.filename}" ?`)) {
      return;
    }

    this.api.deleteImage(image.id).subscribe({
      next: () => {
        this.images = this.images.filter(img => img.id !== image.id);
        this.total--;
        if (this.images.length === 0 && this.currentPage > 1) {
          this.currentPage--;
          this.loadImages();
        }
      },
      error: (error) => {
        console.error('Delete error:', error);
        alert('Erreur lors de la suppression');
      }
    });
  }

  onFilterChange() {
    this.currentPage = 1;
    this.loadImages();
  }

  previousPage() {
    if (this.currentPage > 1) {
      this.currentPage--;
      this.loadImages();
    }
  }

  nextPage() {
    const maxPage = Math.ceil(this.total / this.pageSize);
    if (this.currentPage < maxPage) {
      this.currentPage++;
      this.loadImages();
    }
  }

  get totalPages(): number {
    return Math.ceil(this.total / this.pageSize);
  }
}
