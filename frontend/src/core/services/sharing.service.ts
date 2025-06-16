import {Injectable} from '@angular/core';
import {environment} from 'src/environments/environment';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {GiftShared} from 'src/core/models/gift/gift-shared.model';
import {ApiResponse} from 'src/core/models/api-response.model';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {firstValueFrom} from 'rxjs';

@Injectable({providedIn: 'root'})
export class SharingService {

  private apiUrl = environment.backendBaseUrl + environment.api.partage;

  constructor(private http: HttpClient,) {
  }

  async setGiftRefunded(shared: GiftShared): Promise<ApiResponse<GiftDetailResponse>>{
    const url = `${this.apiUrl}/rembourse`;
    try {
      console.log('[SharingService] Envoi statut remboursement :', shared);
      const gift = await firstValueFrom(
        this.http.patch<GiftDetailResponse>(url, shared, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );

      return {success: true, data: gift};

    } catch (error) {
      console.error('[SharingService] Erreur lors du changement de statut du remboursement', error);
      return {success: false, message: "❌ Impossible de changer le statut du remboursement."};
    }
  }

  async saveAllShares(shared: GiftShared[], giftId: number): Promise<ApiResponse<GiftDetailResponse>>{
    const url = `${this.apiUrl}/${giftId}`;
    try {
      console.log('[SharingService] Modification ou ajout de partages :', shared);
      const gift = await firstValueFrom(
        this.http.put<GiftDetailResponse>(url, shared, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );

      return {success: true, data: gift};

    } catch (error) {
      console.error('[SharingService] Erreur lors de la mise à jour d\'un partage', error);
      return {success: false, message: "❌ Erreur lors de la mise à jour d\'un partage."};
    }
  }

  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('app_kdo.jwt')}`
    });
  }

}
