import {HttpClient} from '@angular/common/http';
import {Injectable} from '@angular/core';
import {Observable} from 'rxjs';

@Injectable({providedIn: 'root'})
export class AccountService {
  constructor(private http: HttpClient) {
  }

  getGroupStatus(): Observable<any> {
    return this.http.get('/groups/choose', {withCredentials: true});

  }
}
