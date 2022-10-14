import { embed } from '@bokeh/bokehjs'

export default function BokehFigure({
    json,
    target
  }: {
    json: embed.JsonItem,
    target: string
  }) {
    embed.embed_item(json, target)
    return (
      <div id={target}></div>
    )
  }
