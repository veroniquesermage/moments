export type Theme = 'dark' | 'light' | 'daltonien' | 'neuroatypique';

export interface ThemeMeta {
  value: Theme;
  label: string;
  description: string;
  histoire: string;
  resume: string
}
