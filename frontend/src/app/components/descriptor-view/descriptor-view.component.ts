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
  Math = Math; // Exposer Math pour l'utiliser dans le template

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
          // Charger les descripteurs détaillés de l'image complète
          this.api.getDescriptors(this.imageId, undefined).subscribe({
            next: (descResp: any) => {
              this.descriptors = descResp.descriptors;
              this.loading = false;
            },
            error: (error) => {
              this.error = `Erreur lors du chargement des descripteurs: ${error.error?.error || error.message}`;
              this.loading = false;
            }
          });
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


  selectedObjectId: number | null = null;
  selectedObjectClass: string | null = null;

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

  /**
   * Charge les descripteurs d'un objet spécifique
   */
  loadObjectDescriptors(objectId: number) {
    this.selectedObjectId = objectId;
    const obj = this.image?.objects_detected?.[objectId];
    this.selectedObjectClass = obj?.class || null;
    
    this.loading = true;
    this.error = null;
    
    this.api.getDescriptors(this.imageId, objectId).subscribe({
      next: (descResp: any) => {
        this.descriptors = descResp.descriptors;
        this.loading = false;
      },
      error: (error) => {
        this.error = `Erreur lors du chargement des descripteurs: ${error.error?.error || error.message}`;
        this.loading = false;
      }
    });
  }

  /**
   * Retourne à l'affichage des descripteurs de l'image complète
   */
  showImageDescriptors() {
    this.selectedObjectId = null;
    this.selectedObjectClass = null;
    this.loadImageData();
  }

  /**
   * Convertit une couleur RGB en hexadécimal
   */
  rgbToHex(r: number, g: number, b: number): string {
    return '#' + [r, g, b].map(x => {
      const hex = Math.round(x).toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    }).join('');
  }

  /**
   * Obtient les statistiques d'un histogramme
   */
  getHistogramStats(hist: number[]): { mean: number, std: number, max: number, min: number } {
    if (!hist || hist.length === 0) {
      return { mean: 0, std: 0, max: 0, min: 0 };
    }
    const mean = hist.reduce((a, b) => a + b, 0) / hist.length;
    const variance = hist.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / hist.length;
    const std = Math.sqrt(variance);
    return {
      mean: mean,
      std: std,
      max: Math.max(...hist),
      min: Math.min(...hist)
    };
  }

  /**
   * Calcule la moyenne d'un tableau
   */
  getArrayMean(arr: number[]): number {
    if (!arr || arr.length === 0) return 0;
    return arr.reduce((a, b) => a + b, 0) / arr.length;
  }

  /**
   * Calcule l'écart-type d'un tableau
   */
  getArrayStd(arr: number[]): number {
    if (!arr || arr.length === 0) return 0;
    const mean = this.getArrayMean(arr);
    const variance = arr.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / arr.length;
    return Math.sqrt(variance);
  }

  /**
   * Obtient le minimum d'un tableau
   */
  getArrayMin(arr: number[]): number {
    if (!arr || arr.length === 0) return 0;
    return Math.min(...arr);
  }

  /**
   * Obtient le maximum d'un tableau
   */
  getArrayMax(arr: number[]): number {
    if (!arr || arr.length === 0) return 0;
    return Math.max(...arr);
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
