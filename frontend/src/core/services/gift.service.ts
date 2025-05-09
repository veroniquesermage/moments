import {Injectable, signal} from '@angular/core';
import {environment} from 'src/environments/environment';
import {GiftDTO} from 'src/core/models/gift-dto.model';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {firstValueFrom} from 'rxjs';
import {Gift} from 'src/core/models/gift.model';
import {GiftMapper} from 'src/core/mapper/gift.mapper';
import {GroupeResume} from 'src/core/models/group-resume.model';

@Injectable({providedIn: 'root'})
export class GiftService {

  private apiUrl = environment.backendBaseUrl + environment.api.cadeaux;
  gifts = signal<Gift[]>([])
  isLoading = signal<boolean>(false);
  errorMessage = signal<string | null>(null);

  constructor(private http: HttpClient,) {
  }

  async fetchGifts(userId?: number): Promise<void> {

    this.isLoading.set(true);
    this.errorMessage.set(null);

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

    } catch (error) {
      console.error('[GiftService] Erreur lors de la récupération des cadeaux', error);
      this.errorMessage.set("❌ Impossible de récupérer les cadeaux.");
    } finally {
      this.isLoading.set(false);
    }

  }

  async createGift(gift: Gift) {

    const giftDTO = GiftMapper.toDTO(gift);

    try {
      const giftCreated = await firstValueFrom(this.http.post<GiftDTO>(this.apiUrl, giftDTO, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      await this.fetchGifts();
    } catch (error) {
      console.error('[GiftService] Erreur lors de la création du cadeau', error);
      this.errorMessage.set("❌ Impossible de créer le cadeau.");
    }
  }

  async getGift(id: number) {

    const idEnc = encodeURIComponent(id);
    const url = `${this.apiUrl}/${idEnc}`;
    try {
      const giftDto = await firstValueFrom(
        this.http.get<GiftDTO>(url, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );

      const gift = GiftMapper.fromDTO(giftDto);

      return {success: true, data: gift};

    } catch (error) {
      console.error('[GiftService] Erreur lors de la récupération du cadeau', error);
      this.errorMessage.set("❌ Impossible de récupérer le cadeau.");
      return {success: false, message: "❌ Impossible de récupérer le cadeau."};
    }

  }

  async deleteGift(id: number) {
    const idEnc = encodeURIComponent(id);
    const url = `${this.apiUrl}/${idEnc}`;

    try {
      await firstValueFrom(
        this.http.delete<GiftDTO>(url, {
          headers: this.getAuthHeaders(),
          withCredentials: true
        })
      );

    } catch (error) {
      console.error('[GiftService] Erreur lors de la suppression du cadeau', error);
      this.errorMessage.set("❌ Impossible de supprimer le cadeau.");
    }

  }

  async updateGift(gift: Gift) {

    const giftDTO = GiftMapper.toDTO(gift);
    const url = `${this.apiUrl}/${gift.id}`;
    try {
      const giftCreated = await firstValueFrom(this.http.put<GiftDTO>(url, giftDTO, {
        headers: this.getAuthHeaders(),
        withCredentials: true
      }));
      await this.fetchGifts();
    } catch (error) {
      console.error('[GiftService] Erreur lors de la création du cadeau', error);
      this.errorMessage.set("❌ Impossible de créer le cadeau.");
    }
  }


  private getAuthHeaders(): HttpHeaders {
    return new HttpHeaders({
      'Authorization': `Bearer ${localStorage.getItem('jwt')}`
    });
  }
}
