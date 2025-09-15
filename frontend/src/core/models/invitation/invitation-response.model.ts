export interface InvitationResponse {
  id: number;
  email: string;
  date_envoi: string;
  envoye_par_nom: string;
  statut: 'EN_ATTENTE' | 'EXPIREE';
}