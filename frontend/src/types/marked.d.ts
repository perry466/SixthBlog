declare module 'marked' {
  export function parse(src: string, options?: MarkedOptions): string
  export function setOptions(options: MarkedOptions): void
  
  export interface MarkedOptions {
    highlight?: (code: string, lang?: string) => string
    breaks?: boolean
    gfm?: boolean
    [key: string]: any
  }
}
