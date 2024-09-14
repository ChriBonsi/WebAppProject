import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {
  username: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(private http: HttpClient, private router: Router) {}

  onSubmit() {
    const registerData = { username: this.username, password: this.password };

    this.http.post<any>('http://127.0.0.1:5000/register', registerData).subscribe(
      response => {
        // Reindirizza al login dopo la registrazione
        this.router.navigate(['/login']);
      },
      error => {
        this.errorMessage = 'Registration failed. Username might already be taken.';
      }
    );
  }
}
