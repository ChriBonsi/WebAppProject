import {Component} from '@angular/core';
import {ConfigurationService} from "../../services/configuration.service";
import {AuthService} from "../../services/auth.service";

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent {
  isModifiable: boolean = false;

  constructor(protected configurationService: ConfigurationService, protected authService: AuthService) {
  }

  /**
   * Handles the switch to the text mode of the title of the project.
   */
  switchToText() {
    this.isModifiable = false;
    this.configurationService.updateContent();
  }

  // Metodo per il logout
  onLogout() {
    this.authService.logout();
  }
}
