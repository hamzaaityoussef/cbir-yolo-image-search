import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { ApiService, Image } from '../../services/api.service';

@Component({
  selector: 'app-descriptor-view',
  templateUrl: './descriptor-view.component.html',
  styleUrls: ['./descriptor-view.component.css']
})
export class DescriptorViewComponent implements OnInit {
  imageId: string = '';
  image: Image | null = null;
  descriptors: any = null;
  loading = false;
  error: string | null = null;

  constructor(
    private route: ActivatedRoute,
    public api: ApiService
  ) {}

  ngOnInit() {
    this.route.params.subscribe(params => {
      this.imageId = params['id'];
      this.loadImageData();
    });
  }

  loadImageData() {
    this.loading = true;
    this.error = null;

    // Récupérer les informations de l'image
    this.api.listImages({ limit: 1000 }).subscribe({
      next: (response) => {
        this.image = response.images.find(img => img.id === this.imageId) || null;
        
        if (this.image) {
          // Pour obtenir les descripteurs complets, on doit faire une recherche
          // ou créer un endpoint dédié. Pour l'instant, on utilise les données disponibles
          this.loadDescriptors();
        } else {
          this.error = 'Image non trouvée';
          this.loading = false;
        }
      },
      error: (error) => {
        this.error = `Erreur: ${error.error?.error || error.message}`;
        this.loading = false;
      }
    });
  }

  loadDescriptors() {
    // Note: Les descripteurs complets ne sont pas retournés par /images
    // Pour une implémentation complète, il faudrait un endpoint /images/:id/descriptors
    // Pour l'instant, on affiche les informations disponibles
    this.loading = false;
  }

  formatNumber(value: number): string {
    if (value === null || value === undefined) return 'N/A';
    if (typeof value === 'number') {
      return value.toFixed(4);
    }
    return String(value);
  }

  formatArray(arr: any[]): string {
    if (!arr || arr.length === 0) return 'Aucune donnée';
    if (arr.length > 10) {
      return `[${arr.length} éléments] - Aperçu: ${arr.slice(0, 5).join(', ')}...`;
    }
    return arr.join(', ');
  }

  goBack() {
    window.history.back();
  }

  downloadImage() {
    if (!this.image) return;
    
    this.api.downloadImage(this.image.id).subscribe({
      next: (blob) => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = this.image!.filename;
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
}
