import 'react-tabulator/lib/styles.css'
import { ReactTabulator, ColumnDefinition } from 'react-tabulator'
import { createPopper, Options } from '@popperjs/core'
import tooltipStyles from './tooltip.module.css'
import { Stats, StatsRow } from '../lib/leagues'

const COLUMN_WIDTH = 60

export default function Table({stats}: {stats: Stats}) {
  const columns = [
    TableColumn(stats, {isHeader: true, title: "Team", field: "team"}),
    TableColumn(stats, {isGroup: true, title: "Scoring", popup: "Points per 100 possessions", columns: [
      TableColumn(stats, {title: "Net", field: "net_scoring_rate", middle: 0}),
      TableColumn(stats, {title: "Off", field: "off_scoring_rate"}),
      TableColumn(stats, {title: "Def", field: "def_scoring_rate", reverse: true, cssClass: "tabulator-cell-col-right"}),
    ]}),
    TableColumn(stats, {isGroup: true, title: "Pace", popup: "Possessions per 48 minutes", columns: [
      TableColumn(stats, {title: "Net", field: "total_pace", cssClass: "tabulator-cell-col-left"}),
      TableColumn(stats, {title: "Off", field: "off_pace"}),
      TableColumn(stats, {title: "Def", field: "def_pace", cssClass: "tabulator-cell-col-right"}),
    ]}),
    TableColumn(stats, {isGroup: true, title: "Offense", columns: [
      TableColumn(stats, {title: "3pt Fq", field: "off_three_attempt_rate", popup: "Percentage of shots attempted from 3", cssClass: "tabulator-cell-col-left"}),
      TableColumn(stats, {title: "2pt%", field: "off_two_make_rate", popup: "2pt shooting percentage"}),
      TableColumn(stats, {title: "3pt%", field: "off_three_make_rate", popup: "3pt shooting percentage"}),
      TableColumn(stats, {title: "Reb%", field: "off_reb_rate", popup: "Percentage of misses rebounded"}),
      TableColumn(stats, {title: "Tov/100", field: "off_turnover_rate", reverse: true, popup: "Turnovers per 100 possessions"}),
      TableColumn(stats, {title: "FT/100", field: "off_ft_attempt_rate", popup: "Free throws attempted per 100 possessions"}),
      TableColumn(stats, {title: "FT%", field: "off_ft_make_rate", popup: "Free throw shooting percentage", cssClass: "tabulator-cell-col-right"}),
    ]}),
    TableColumn(stats, {isGroup: true, title: "Defense", columns: [
      TableColumn(stats, {title: "3pt Fq", field: "def_three_attempt_rate", reverse: true, popup: "Percentage of shots conceded from 3", cssClass: "tabulator-cell-col-left"}),
      TableColumn(stats, {title: "2pt%", field: "def_two_make_rate", reverse: true, popup: "Opponent 2pt shooting percentage"}),
      TableColumn(stats, {title: "3pt%", field: "def_three_make_rate", reverse: true, popup: "Opponent 3pt shooting percentage"}),
      TableColumn(stats, {title: "Reb%", field: "def_reb_rate", reverse: true, popup: "Percentage of opponent misses rebounded"}),
      TableColumn(stats, {title: "Tov/100", field: "def_turnover_rate", popup: "Turnovers forced per 100 possessions"}),
      TableColumn(stats, {title: "FT/100", field: "def_ft_attempt_rate", reverse: true, popup: "Free throws conceded per 100 possessions"}),
    ]}),
  ] as ColumnDefinition[]
  return (
    <ReactTabulator
      data={stats}
      columns={columns}
      layout="fitData"
      options={
        {
          columnHeaderVertAlign: "bottom",
          frozenRows: 1,
          maxHeight: "85vh",
        }
      }
    />
  )
}

function CellFormatter(stats: Stats, reverse: boolean, middle?: number) {
  return (cell: any, formatterParams: {}, onRendered: any) => {
    const field = cell.getColumn().getField()
    const vals = stats.map((row: StatsRow) => row[field] as number)
    let min = Math.min(...vals)
    let max = Math.max(...vals)
    if (middle === undefined) {
      middle = vals.reduce((a: number, b: number) => a + b) / vals.length
    }
    const cellValue = cell.getValue()
    let alpha
    let backgroundColor
    if (cellValue > middle) {
      alpha = (cellValue - middle) / (max - middle)
      if (reverse) {
        backgroundColor = `hsla(2, 70%, 70%, ${alpha})`
      } else {
        backgroundColor = `hsla(182, 80%, 50%, ${alpha})`
      }
    } else {
      alpha = (middle - cellValue) / (middle - min)
      if (reverse) {
        backgroundColor = `hsla(182, 80%, 50%, ${alpha})`
      } else {
        backgroundColor = `hsla(2, 70%, 70%, ${alpha})`
      }
    }
    let cellElement = cell.getElement()
    cellElement.style.backgroundColor = backgroundColor
    return cellValue.toFixed(1) as string
  }
}

function TitleFormatter(hoverText: string) {
  return (cell: any, formatterParams: {}, onRendered: any) => {
    const titleElement = cell.getElement()
    const arrow = document.createElement("div")
    arrow.classList.add(tooltipStyles.arrow)
    arrow.setAttribute("data-popper-arrow", "")
    const tooltip = document.createElement("div")
    tooltip.classList.add(tooltipStyles.tooltip)
    tooltip.setAttribute("role", "tooltip")
    tooltip.appendChild(document.createTextNode(hoverText))
    tooltip.appendChild(arrow)
    document.body.insertBefore(tooltip, null)
    const popperInst = createPopper(titleElement, tooltip, {
      placement: "top",
      modifiers: [
        {
          name: 'offset',
          options: {
            offset: [0, 8],
          },
        },
      ],
    })

    function show() {
      tooltip.setAttribute('data-show', '')
      popperInst.setOptions((options: Partial<Options>) => ({
        ...options,
        modifiers: [
          ...options.modifiers,
          { name: 'eventListeners', enabled: true },
        ],
      }))
      popperInst.update()
    }

    function hide() {
      tooltip.removeAttribute('data-show');
      popperInst.setOptions((options: Partial<Options>) => ({
        ...options,
        modifiers: [
          ...options.modifiers,
          { name: 'eventListeners', enabled: false },
        ],
      }))
    }

    titleElement.onmouseover = show
    titleElement.onmouseleave = hide
    titleElement.onfocus = show
    titleElement.onblur = hide
    return cell.getValue() as string
  }
}

function ReverseSorter(a: number, b: number, aRow: any, bRow: any, column: any, dir: string, sorterParams: {}) {
  return b - a
}

function TableColumn(stats: Stats, {
  isHeader = false,
  isGroup = false,
  popup,
  reverse = false,
  middle,
  ...props
}: {
  isHeader?: boolean,
  isGroup?: boolean,
  popup?: string,
  reverse?: boolean,
  middle?: number,
  [index: string]: any,
}) {
  const column = {resizable: false, headerHozAlign: "center", ...props} as ColumnDefinition
  if (popup !== undefined) {
    column["titleFormatter"] = TitleFormatter(popup)
  }
  if (isHeader) {
    column["frozen"] = true
    column["headerSort"] = false
  }
  else if (isGroup) {
  }
  else {
    column["width"] = COLUMN_WIDTH
    column["hozAlign"] = "center"
    if (reverse) {
      column["sorter"] = ReverseSorter
    }
    column["headerSortTristate"] = true
    column["headerSortStartingDir"] = "desc"
    column["formatter"] = CellFormatter(stats, reverse, middle)
  }
  return column
}
