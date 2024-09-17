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

  constructor(private http: HttpClient, private router: Router) {
  }

  onSubmit() {
    // Controlli lato client
    if (!this.username.trim() || !this.password.trim()) {
      this.errorMessage = 'Username and/or password cannot be empty.';
      return;
    }

    if (this.username.length < 3) {
      this.errorMessage = 'Username must be at least 3 characters long.';
      return;
    }

    if (this.password.length < 6) {
      this.errorMessage = 'Password must be at least 6 characters long.';
      return;
    }

    const registerData = {username: this.username, password: this.password};

    this.http.post<any>('http://127.0.0.1:5000/register', registerData).subscribe(
      response => {
        // Reindirizza al login dopo la registrazione
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
