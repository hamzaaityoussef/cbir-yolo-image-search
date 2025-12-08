import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { RouterModule, Routes } from '@angular/router';

import { AppComponent } from './app.component';
import { ImageUploadComponent } from './components/image-upload/image-upload.component';
import { ImageGalleryComponent } from './components/image-gallery/image-gallery.component';
import { ImageSearchComponent } from './components/image-search/image-search.component';
import { DescriptorViewComponent } from './components/descriptor-view/descriptor-view.component';

const routes: Routes = [
  { path: '', component: ImageUploadComponent },
  { path: 'gallery', component: ImageGalleryComponent },
  { path: 'search', component: ImageSearchComponent },
  { path: 'descriptors/:id', component: DescriptorViewComponent }
];

@NgModule({
  declarations: [
    AppComponent,
    ImageUploadComponent,
    ImageGalleryComponent,
    ImageSearchComponent,
    DescriptorViewComponent
  ],
  imports: [
    BrowserModule,
    HttpClientModule,
    FormsModule,
    RouterModule.forRoot(routes)
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

