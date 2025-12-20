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
  pageSize = 21;
  total = 0;

  // Filtres
  objectClassFilter = '';
  availableClasses: string[] = [];

  // Pour la sélection multiple
  selectedImages: Image[] = [];

  // Pour la transformation d'image
  showTransformModal = false;
  transformTarget: Image | null = null;
  transformType: string = 'crop';
  transformParams: any = {};
  transformError: string | null = null;
  transformSuccess: boolean = false;

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadImages();
  }

  loadImages() {
    this.loading = true;
    this.error = null;
    this.api.getImages(this.currentPage, this.pageSize, this.objectClassFilter).subscribe({
      next: (response: any) => {
        this.images = response.images;
        this.total = response.total;
        this.extractAvailableClasses();
        this.loading = false;
      },
      error: (err: any) => {
        this.error = 'Erreur lors du chargement des images';
        this.loading = false;
      }
    });
  }

  onImageSelectChange(image: Image) {
    if (image.selected) {
      if (!this.selectedImages.includes(image)) {
        this.selectedImages.push(image);
      }
    } else {
      this.selectedImages = this.selectedImages.filter(img => img.id !== image.id);
    }
  }

  deleteSelectedImages() {
    if (this.selectedImages.length === 0) return;
    if (!confirm(`Supprimer ${this.selectedImages.length} image(s) sélectionnée(s) ?`)) return;
    let count = 0;
    this.selectedImages.forEach(img => {
      this.api.deleteImage(img.id).subscribe({
        next: () => {
          count++;
          this.images = this.images.filter(i => i.id !== img.id);
          if (count === this.selectedImages.length) {
            this.selectedImages = [];
            this.loadImages();
          }
        },
        error: (error) => {
          console.error('Delete error:', error);
        }
      });
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

  openTransformModal(image: Image) {
    this.transformTarget = image;
    this.showTransformModal = true;
    this.transformType = 'crop';
    this.transformParams = {};
    this.transformError = null;
    this.transformSuccess = false;
  }

  closeTransformModal() {
    this.showTransformModal = false;
    this.transformTarget = null;
    this.transformType = 'crop';
    this.transformParams = {};
    this.transformError = null;
    this.transformSuccess = false;
  }

  submitTransform() {
    if (!this.transformTarget) {
      this.transformError = 'Aucune image sélectionnée';
      return;
    }

    this.transformError = null;
    this.transformSuccess = false;

    // Préparer les paramètres selon le type de transformation
    const params: any = {};
    
    if (this.transformType === 'crop') {
      params.x = parseInt(this.transformParams.x) || 0;
      params.y = parseInt(this.transformParams.y) || 0;
      params.width = parseInt(this.transformParams.width) || 100;
      params.height = parseInt(this.transformParams.height) || 100;
    } else if (this.transformType === 'resize') {
      if (this.transformParams.scale) {
        params.scale = parseFloat(this.transformParams.scale) || 1.0;
      } else {
        params.width = parseInt(this.transformParams.width) || 800;
        params.height = parseInt(this.transformParams.height) || 600;
      }
    } else if (this.transformType === 'rotate') {
      params.angle = parseFloat(this.transformParams.angle) || 0;
    } else if (this.transformType === 'flip') {
      params.direction = this.transformParams.direction || 'horizontal';
    } else if (this.transformType === 'brightness') {
      params.brightness = parseFloat(this.transformParams.brightness) || 1.0;
      params.contrast = parseFloat(this.transformParams.contrast) || 1.0;
    }

    // Appeler l'API
    this.api.transform(this.transformTarget.id, this.transformType, params).subscribe({
      next: (response: any) => {
        this.transformSuccess = true;
        // Recharger la liste des images après un court délai
        setTimeout(() => {
          this.loadImages();
          this.closeTransformModal();
        }, 1500);
      },
      error: (error: any) => {
        this.transformError = error.error?.error || 'Erreur lors de la transformation';
        console.error('Transform error:', error);
      }
    });
  }
}
