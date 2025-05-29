import {Injectable, signal} from '@angular/core';
import {environment} from 'src/environments/environment';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {firstValueFrom} from 'rxjs';
import {GiftMapper} from 'src/core/mapper/gift.mapper';
import {GiftAction} from 'src/core/enum/gift-action.enum';
import {EligibilityResponseDto} from 'src/core/models/eligibility-response-dto.model';
import {ApiResponse} from 'src/core/models/api-response.model';
import {Gift} from 'src/core/models/gift/gift.model';
import {GiftDTO} from 'src/core/models/gift/gift-dto.model';
import {GiftDetailResponse} from 'src/core/models/gift/gift-detail-response.model';
import {GiftStatutDTO} from 'src/core/models/gift/gift-statut.model';
import {GiftPriority} from 'src/core/models/gift/gift-priority.model';

@Injectable({providedIn: 'root'})
export class GiftService {

  private apiUrl = environment.backendBaseUrl + environment.api.cadeaux;
  gifts = signal<Gift[]>([])
  isLoading = signal<boolean>(false);

  constructor(private http: HttpClient,) {
  }

  async fetchGifts(userId?: number): Promise<ApiResponse<Gift[]>> {

    this.isLoading.set(true);

    let params = new HttpParams();
    if (userId != null) {
      params = params.set('userId', userId.toString());
    }

    try {
      const giftsDto = await firstValueFrom(
        this.http.get<GiftDTO[]>(this.apiUrl, {
          headers: this.getAuthHeaders(),
          params: params,
          withCredentials: true
        })
      );

      const result: Gift[] = giftsDto.map(dto => GiftMapper.fromDTO(dto));
      this.gifts.set(result);

      return {success: true, data: result};

    } catch (error) {
      console.error('[GiftService] Erreur lors de la récupération des cadeaux', error);

      return {success: false, message: "Impossible de récupérer les cadeaux."};
    } finally {
      this.isLoading.set(false);
    }

  }

  async createGift(gift: Gift): Promise<ApiResponse<Gift>> {

    const giftDTO = GiftMapper.toDTO(gift);

    try {
      const giftDto = await firstValueFrom(this.http.post<GiftDTO>(this.apiUrl, giftDTO, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      await this.fetchGifts();

      const result: Gift = GiftMapper.fromDTO(giftDto);
      return {success: true, data: result};
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
        this.http.delete<GiftDTO>(url, {
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

  async updateGift(gift: Gift): Promise<ApiResponse<Gift>> {

    const giftDTO = GiftMapper.toDTO(gift);
    const url = `${this.apiUrl}/${gift.id}`;
    try {
      const result = await firstValueFrom(this.http.put<GiftDTO>(url, giftDTO, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));

      const gift = GiftMapper.fromDTO(result);

      return {success: true, data: gift};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la création du cadeau', error);
      return {success: false, message: "❌ Impossible de créer le cadeau."};
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

  async changeStatusGift(id: number, status: GiftStatutDTO): Promise<ApiResponse<Gift>> {

    const idEnc = encodeURIComponent(id);
    const url = `${this.apiUrl}/${idEnc}/changer-statut`;
    try {
      const giftDto = await firstValueFrom(
        this.http.put<GiftDTO>(url, status, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );
      const gift = GiftMapper.fromDTO(giftDto);
      return {success: true, data: gift};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la réservation du cadeau', error);
      return {success: false, message: "❌ Impossible de réserver le cadeau."};
    }
  }

  async getFollowedGifts(): Promise<ApiResponse<Gift[]>> {
    const url = `${this.apiUrl}/suivis`;
    try {
      const giftsDto = await firstValueFrom(
        this.http.get<GiftDTO[]>(url, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );

      const result: Gift[] = giftsDto.map(dto => GiftMapper.fromDTO(dto));
      this.gifts.set(result);
      return {success: true, data: result};

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

  async updateAllGifts(gifts: GiftPriority[]): Promise<ApiResponse<Gift[]>> {
    try {
      const giftsList = await firstValueFrom(this.http.put<Gift[]>(this.apiUrl, gifts, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));

      const result: Gift[] = giftsList.map(dto => GiftMapper.fromDTO(dto));
      this.gifts.set(result);
      return {success: true, data: result};
    } catch (error) {
      console.error('[GiftService] Erreur lors de la mise à jour des priorités', error);

      return {success: false, message: "❌ Impossible mettre à jour les priorités."};
    }
  }

  clearGifts() {
    this.gifts.set([]);
  }

  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('jwt')}`
    });
  }

}
