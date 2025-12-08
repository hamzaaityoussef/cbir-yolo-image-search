import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-descriptor-view',
  templateUrl: './descriptor-view.component.html',
  styleUrls: ['./descriptor-view.component.css']
})
export class DescriptorViewComponent {
  @Input() descriptors: any = {};
}

