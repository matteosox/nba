import fs from 'fs'
import path from 'path'
import { parse } from '@vanillaes/csv';

const seasonsDirectory = path.join(process.cwd(), 'public', 'seasons')

export function getAllSeasons() {
  const seasons = fs.readdirSync(seasonsDirectory)
  return seasons.map(season => {
    return {
      params: {
        season
      }
    }
  })
}

export function getSeasonData(season: string) {
  const seasonDir = path.join(seasonsDirectory, season)
  const statsFile = path.join(seasonDir, `team_stats_nba_${season}_Regular Season.csv`)
  const statsStr = fs.readFileSync(statsFile, 'utf8')
  const stats = parse(statsStr).map(row => {
    return row.map( val => {
      return parseFloat(val) ? parseFloat(val as string).toFixed(1) : val
    })
  })
  return {
    season,
    stats,
    ratingsImage: `/seasons/${season}/team_ratings_nba_${season}_Regular Season.png`,
    pacesImage: `/seasons/${season}/team_paces_nba_${season}_Regular Season.png`
  }
}
