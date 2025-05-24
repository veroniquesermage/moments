export interface GiftTableColumn {
  key: string;
  label?: string;
  formatFn?: (value: any, gift: any) => string;
}
