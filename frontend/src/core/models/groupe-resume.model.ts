export interface GroupeResume {
  id: number;
  nomGroupe: string;
  description: string;
  role: string;
  dateAjout: string; // ou Date si tu fais un parse() plus tard
}
