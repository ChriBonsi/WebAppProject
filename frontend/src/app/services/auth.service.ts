import {Injectable} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {Router} from "@angular/router";

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://localhost:5000';  // URL del tuo backend

  constructor(private http: HttpClient, private router: Router) {
  }

  login(username: string, password: string): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/login`, {username, password});
  }

  register(username: string, password: string) {
    return this.http.post<any>(`${this.apiUrl}/register`, {username, password});
  }

  logout() {
    // Rimuove il token
    localStorage.removeItem('token');
    this.router.navigate(['/login']); // Reindirizza alla pagina di login
  }

  isLoggedIn(): boolean {
    return !!localStorage.getItem('token');
  }
}
