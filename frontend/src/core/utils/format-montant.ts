export const formatEuro = (v: number | null | undefined): string =>
  v != null
    ? `${new Intl.NumberFormat('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(v)}`
    : '-';
