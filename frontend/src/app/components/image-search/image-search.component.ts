import { Component } from '@angular/core';
import { ApiService } from '../../services/api.service';

@Component({
  selector: 'app-image-search',
  templateUrl: './image-search.component.html',
  styleUrls: ['./image-search.component.css']
})
export class ImageSearchComponent {
  queryFile: File | null = null;
  results: any[] = [];

  constructor(private api: ApiService) {}

  onQueryChange(event: any) {
    const files: FileList = event.target.files;
    this.queryFile = files && files.length > 0 ? files[0] : null;
  }

  search() {
    // Placeholder : la logique réelle doit envoyer le fichier + params au backend
    this.api.search({ query: 'placeholder' }).subscribe((res) => {
      this.results = res.results || [];
    });
  }
}

