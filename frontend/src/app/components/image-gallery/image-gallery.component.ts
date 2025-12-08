import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-image-gallery',
  templateUrl: './image-gallery.component.html',
  styleUrls: ['./image-gallery.component.css']
})
export class ImageGalleryComponent {
  images: any[] = [];

  constructor(private api: ApiService) {
    // TODO: remplacer par un endpoint dédié listant les images
    this.api.search({}).subscribe((data) => (this.images = data.results || []));
  }

  download(id: string) {
    this.api.downloadImage(id).subscribe();
  }

  remove(id: string) {
    this.api.deleteImage(id).subscribe(() => {
      this.images = this.images.filter((img) => img.id !== id);
    });
  }
}

