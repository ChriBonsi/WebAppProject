import {Injectable} from '@angular/core';
import {CanActivate, Router} from '@angular/router';

@Injectable({
  providedIn: 'root',
})
export class AuthGuard implements CanActivate {
  constructor(private router: Router) {
  }

  canActivate(): boolean {
    const token = localStorage.getItem('token');

    // Se il token esiste, permette l'accesso
    if (token) {
      return true;
    } else {
      // Se il token non esiste, reindirizza alla pagina di login
      this.router.navigate(['/login']);
      return false;
    }
  }
}
