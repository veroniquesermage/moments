export interface GiftIdeaFormData {
  id?: number
  nom: string;
  marque?: string;
  magasin?: string;
  description?: string;
  url?: string;
  quantite: number;
  prix?: number;
  fraisPort?: number;
  commentaire?: string;
  destinataireId: number;
}
