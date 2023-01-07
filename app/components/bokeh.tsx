import { useEffect } from 'react'
import { embed } from '@bokeh/bokehjs'

export default function BokehFigure({
    json,
    target,
    style
  }: {
    json: embed.JsonItem,
    target: string,
    style: object
  }) {
    useEffect(() => {
      for (const elem of document.getElementById(target).children)
        elem.remove()
      embed.embed_item(json, target)
    });
    return (
      <div className="bk-root" id={target} style={style}></div>
    )
  }
