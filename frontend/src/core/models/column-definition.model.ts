export type FormatFn = (value: any) => string;

export interface ColumnDefinition {
  key: string;
  label: string;
  formatFn?: FormatFn;
}
