import {Component} from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Router} from '@angular/router';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent {
  username: string = '';
  password: string = '';
  errorMessage: string = '';

  constructor(private http: HttpClient, private router: Router) {
  }

  onSubmit() {
    const loginData = {username: this.username, password: this.password};

    this.http.post<any>('http://127.0.0.1:5000/login', loginData).subscribe(
      response => {
        console.log(response.token);  // Verifica il token qui
        localStorage.setItem('token', response.token);
        this.router.navigate(['/']);
      },
      error => {
        this.errorMessage = 'Combination of username and password is incorrect';
      }
    );
  }
}
