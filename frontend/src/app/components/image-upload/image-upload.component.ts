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
  messageType: 'success' | 'error' | 'info' = 'info';
  uploading = false;
  uploadProgress: { [key: string]: number } = {};

  constructor(private api: ApiService) {}

  get filesArray(): File[] {
    return this.selectedFiles ? Array.from(this.selectedFiles) : [];
  }

  onFileChange(event: any) {
    const files = event.target.files;
    if (files && files.length > 0) {
      this.selectedFiles = files;
      this.message = `${files.length} fichier(s) sélectionné(s)`;
      this.messageType = 'info';
    }
  }

  upload() {
    if (!this.selectedFiles || this.selectedFiles.length === 0) {
      this.message = 'Veuillez sélectionner au moins un fichier.';
      this.messageType = 'error';
      return;
    }

    // Vérifier les extensions
    const allowedExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp'];
    const invalidFiles: string[] = [];
    
    Array.from(this.selectedFiles).forEach(file => {
      const ext = file.name.split('.').pop()?.toLowerCase();
      if (!ext || !allowedExtensions.includes(ext)) {
        invalidFiles.push(file.name);
      }
    });

    if (invalidFiles.length > 0) {
      this.message = `Fichiers invalides: ${invalidFiles.join(', ')}. Extensions autorisées: ${allowedExtensions.join(', ')}`;
      this.messageType = 'error';
      return;
    }

    this.uploading = true;
    this.message = 'Upload en cours...';
    this.messageType = 'info';

    this.api.uploadImages(this.selectedFiles).subscribe({
      next: (response) => {
        this.uploading = false;
        const uploadedCount = response.uploaded?.length || 0;
        const errorCount = response.errors?.length || 0;
        
        if (uploadedCount > 0) {
          this.message = `${uploadedCount} image(s) uploadée(s) avec succès.`;
          if (errorCount > 0) {
            this.message += ` ${errorCount} erreur(s).`;
            this.messageType = 'error';
          } else {
            this.messageType = 'success';
          }
          
          // Réinitialiser le formulaire
          this.selectedFiles = null;
          const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
          if (fileInput) fileInput.value = '';
        } else {
          this.message = 'Aucune image n\'a pu être uploadée.';
          this.messageType = 'error';
        }
      },
      error: (error) => {
        this.uploading = false;
        this.message = `Erreur lors de l'upload: ${error.error?.error || error.message || 'Erreur inconnue'}`;
        this.messageType = 'error';
        console.error('Upload error:', error);
      }
    });
  }

  getMessageClass(): string {
    return `message message-${this.messageType}`;
  }
}
