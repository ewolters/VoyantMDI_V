declare namespace ExcelScript {
  interface Range { getValues(): (string | number | boolean)[][]; }
  interface Worksheet { getName(): string; getRange(address?: string): Range; }
  interface Workbook { getName(): string; getWorksheets(): Worksheet[]; }
}
