import {Component} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Router} from '@angular/router';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss']
})
export class RegisterComponent {
  username: string = '';
  password: string = '';
  errorMessage: string = '';
  showPassword: boolean = false;  // Variabile per mostrare/nascondere la password

  constructor(private http: HttpClient, private router: Router) {
  }

  sanitizeInput(input: string): string {
    return input.replace(/[^a-zA-Z0-9_.-]/g, '');  // Solo lettere, numeri, underscore, punti e trattini
  }

  togglePasswordVisibility() {
    this.showPassword = !this.showPassword;
  }

  onSubmit() {
    const sanitizedUsername = this.sanitizeInput(this.username);
    const sanitizedPassword = this.sanitizeInput(this.password);

    // Controlli lato client
    if (!sanitizedUsername.trim() || !sanitizedPassword.trim()) {
      this.errorMessage = 'Username and/or password cannot be empty.';
      return;
    }

    if (sanitizedUsername.length < 3) {
      this.errorMessage = 'Username must be at least 3 characters long.';
      return;
    }

    if (sanitizedPassword.length < 6) {
      this.errorMessage = 'Password must be at least 6 characters long.';
      return;
    }

    const registerData = {username: sanitizedUsername, password: sanitizedPassword};

    this.http.post<any>('http://127.0.0.1:5000/register', registerData).subscribe(
      response => {
        this.router.navigate(['/login']);
      },
      error => {
        if (error.status === 400 && error.error.message === 'Username already exists') {
          this.errorMessage = 'Username is already taken.';
        } else {
          this.errorMessage = 'Registration failed. Please try again.';
        }
      }
    );
  }
}
