import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-image-upload',
  templateUrl: './image-upload.component.html',
  styleUrls: ['./image-upload.component.css']
})
export class ImageUploadComponent {
  selectedFiles: FileList | null = null;
  message = '';

  constructor(private api: ApiService) {}

  onFileChange(event: any) {
    this.selectedFiles = event.target.files;
  }

  upload() {
    if (!this.selectedFiles) {
      this.message = 'Aucun fichier sélectionné.';
      return;
    }
    this.api.uploadImages(this.selectedFiles).subscribe({
      next: () => (this.message = 'Upload réussi.'),
      error: () => (this.message = "Erreur d'upload.")
    });
  }
}

