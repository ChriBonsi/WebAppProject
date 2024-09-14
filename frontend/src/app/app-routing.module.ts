import {NgModule} from '@angular/core';
import {RouterModule, Routes} from '@angular/router';
import {HomepageComponent} from "./components/homepage/homepage.component";
import {WorkspaceComponent} from "./components/workspace/workspace.component";
import {LoginComponent} from './components/login/login.component';
import {RegisterComponent} from './components/register/register.component';
import {AuthGuard} from './auth.guard';

const routes: Routes = [
  {path: '', title: "Homepage", component: HomepageComponent, canActivate: [AuthGuard]},
  {path: 'new', title: "New Project", component: WorkspaceComponent, canActivate: [AuthGuard]},
  {path: 'login', title: "Login", component: LoginComponent},
  {path: 'register', title: "Register", component: RegisterComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule]
})
export class AppRoutingModule {
}
