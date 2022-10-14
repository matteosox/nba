import { embed } from '@bokeh/bokehjs'

export function loadJSON(json_str: string) {
  return JSON.parse(json_str) as embed.JsonItem
}
