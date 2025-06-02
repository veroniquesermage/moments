import {Injectable, signal} from '@angular/core';
import {environment} from 'src/environments/environment';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {firstValueFrom} from 'rxjs';
import {GiftAction} from 'src/core/enum/gift-action.enum';
import {EligibilityResponseDto} from 'src/core/models/eligibility-response-dto.model';
import {ApiResponse} from 'src/core/models/api-response.model';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {GiftStatutDTO} from 'src/core/models/gift/gift-statut.model';
import {GiftPriority} from 'src/core/models/gift/gift-priority.model';
import {GroupStateService} from 'src/core/services/group-state.service';
import {GiftResponse} from 'src/core/models/gift/gift-response.model';
import {GiftCreate} from 'src/core/models/gift/gift-create.model';
import {GiftUpdate} from 'src/core/models/gift/gift-update.model';
import {GiftPublicResponse} from 'src/core/models/gift/gift-public-response.model';
import {GiftDeliveryUpdate} from 'src/core/models/gift/gift-delivery-update.model';
import {GiftFollowed} from 'src/core/models/gift/gift-followed.model';
import {GroupContextService} from 'src/core/services/group-context.service';

@Injectable({providedIn: 'root'})
export class GiftService {

  private apiUrl = environment.backendBaseUrl + environment.api.cadeaux;
  giftsResponse = signal<GiftResponse[]>([])
  giftsFollowed = signal<GiftFollowed[]>([])
  isLoading = signal<boolean>(false);

  constructor(private http: HttpClient,
              private groupContextService: GroupContextService) {
  }

  async fetchGifts(userId?: number): Promise<ApiResponse<GiftResponse[]>> {

    this.isLoading.set(true);

    let params = new HttpParams();
    if (userId != null) {
      params = params.set('userId', userId.toString());
    }

    try {
      const giftsResponse = await firstValueFrom(
        this.http.get<GiftResponse[]>(this.apiUrl, {
          headers: this.getAuthHeaders(),
          params: params,
          withCredentials: true
        })
      );

      this.giftsResponse.set(giftsResponse);

      return {success: true, data: giftsResponse};

    } catch (error) {
      console.error('[GiftService] Erreur lors de la récupération des cadeaux', error);

      return {success: false, message: "Impossible de récupérer les cadeaux."};
    } finally {
      this.isLoading.set(false);
    }

  }

  async getVisibleGiftsForMember(userId: number): Promise<ApiResponse<GiftPublicResponse[]>> {
    const idEnc = encodeURIComponent(userId);
    const url = `${this.apiUrl}/membre/${idEnc}`;
    try {
      const giftsResponse = await firstValueFrom(
        this.http.get<GiftPublicResponse[]>(url, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );
      return {success: true, data: giftsResponse};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la récupération des cadeaux d\'un membre', error);
      return {success: false, message: "❌ Impossible de créer le cadeau."};
    }

  }

  async createGift(gift: GiftCreate): Promise<ApiResponse<GiftResponse>> {
    try {
      const giftResponse = await firstValueFrom(this.http.post<GiftResponse>(this.apiUrl, gift, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      await this.fetchGifts();

      return {success: true, data: giftResponse};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la création du cadeau', error);

      return {success: false, message: "❌ Impossible de créer le cadeau."};
    }
  }

  async getGift(id: number): Promise<ApiResponse<GiftDetailResponse>> {

    const idEnc = encodeURIComponent(id);
    const url = `${this.apiUrl}/${idEnc}`;
    try {
      const gift = await firstValueFrom(
        this.http.get<GiftDetailResponse>(url, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );
      return {success: true, data: gift};

    } catch (error) {
      console.error('[GiftService] Erreur lors de la récupération du cadeau', error);
      return {success: false, message: "❌ Impossible de récupérer le cadeau."};
    }

  }

  async deleteGift(id: number): Promise<ApiResponse<void>> {
    const idEnc = encodeURIComponent(id);
    const url = `${this.apiUrl}/${idEnc}`;

    try {
      await firstValueFrom(
        this.http.delete<GiftResponse>(url, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );
      return {success: true, data: undefined};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la suppression du cadeau', error);
      return {success: false, message: "❌ Impossible de supprimer le cadeau."};
    }

  }

  async updateGift(gift: GiftUpdate): Promise<ApiResponse<GiftResponse>> {

    const url = `${this.apiUrl}/${gift.id}`;
    try {
      const result = await firstValueFrom(this.http.put<GiftResponse>(url, gift, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));

      return {success: true, data: result};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la création du cadeau', error);
      return {success: false, message: "❌ Impossible de créer le cadeau."};
    }
  }

  async updateGiftDelivery(giftId: number, giftUpdate: GiftDeliveryUpdate): Promise<ApiResponse<GiftDeliveryUpdate>> {

    const idEnc = encodeURIComponent(giftId);
    const url = `${this.apiUrl}/${idEnc}/livraison`;

    try {
      const result = await firstValueFrom(this.http.put<GiftDeliveryUpdate>(url, giftUpdate, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));

      return {success: true, data: result};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la mise à jour de la livraison', error);
      return {success: false, message: "❌ Impossible de mettre à jour de la livraison."};
    }
  }

  async getEligibilityForGift(id: number, action: GiftAction): Promise<ApiResponse<EligibilityResponseDto>> {

    const idEnc = encodeURIComponent(id);
    const url = `${this.apiUrl}/${idEnc}/eligibilite?action=${action}`;
    try {
      const eligibilityResponseDto = await firstValueFrom(
        this.http.get<EligibilityResponseDto>(url, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );
      return {success: true, data: eligibilityResponseDto};

    } catch (error) {
      console.error('Erreur pendant la vérification d’éligibilité', error);
      return {success: false, message: "Erreur de communication avec le serveur"};
    }

  }

  async changeStatusGift(id: number, status: GiftStatutDTO): Promise<ApiResponse<GiftResponse>> {

    const idEnc = encodeURIComponent(id);
    const url = `${this.apiUrl}/${idEnc}/changer-statut`;
    try {
      const giftResponse = await firstValueFrom(
        this.http.put<GiftResponse>(url, status, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );
      return {success: true, data: giftResponse};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la réservation du cadeau', error);
      return {success: false, message: "❌ Impossible de réserver le cadeau."};
    }
  }

  async getFollowedGifts(): Promise<ApiResponse<GiftFollowed[]>> {
    const groupId = this.groupContextService.getGroupId()!;
    const idEnc = encodeURIComponent(groupId);
    const url = `${this.apiUrl}/suivis/${idEnc}`;
    try {
      const giftsFollowed = await firstValueFrom(
        this.http.get<GiftFollowed[]>(url, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );

      this.giftsFollowed.set(giftsFollowed);
      return {success: true, data: giftsFollowed};

    } catch (error) {
      console.error('[GiftService] Erreur lors de la récupération des cadeaux suivis', error);
      return {success: false, message: "❌ Impossible de récupérer les cadeaux suivis."};
    }
  }

  async setGiftReceived(id: number, recu: boolean): Promise<ApiResponse<GiftDetailResponse>> {
    const idEnc = encodeURIComponent(id);
    const url = `${this.apiUrl}/${idEnc}/recu`;
    try {
      const gift = await firstValueFrom(
        this.http.patch<GiftDetailResponse>(url, {recu}, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );

      return {success: true, data: gift};

    } catch (error) {
      console.error('[GiftService] Erreur lors du changement de statut de la réception', error);
      return {success: false, message: "❌ Impossible de changer le statut de la réception."};
    }
  }

  async updateAllGifts(gifts: GiftPriority[]): Promise<ApiResponse<GiftResponse[]>> {
    try {
      const giftsList = await firstValueFrom(this.http.put<GiftResponse[]>(this.apiUrl, gifts, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));

      this.giftsResponse.set(giftsList);
      return {success: true, data: giftsList};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la mise à jour des priorités', error);

      return {success: false, message: "❌ Impossible mettre à jour les priorités."};
    }
  }

  clearGifts() {
    this.giftsResponse.set([]);
  }

  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('jwt')}`
    });
  }

}
