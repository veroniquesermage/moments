import { UserDisplay } from 'src/core/models/user-display.model';

export function getDisplayName(user: UserDisplay | null | undefined): string {
  return user?.surnom || user?.prenom || '—';
}
