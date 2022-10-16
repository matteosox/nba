import { parse } from '@vanillaes/csv'
import { load } from 'js-yaml'
import { getObjectString, listKeys } from '../lib/aws_s3'
import { AWS_S3_REGION, AWS_S3_BUCKET, AWS_S3_ROOT_KEY } from '../lib/constants'
import {loadJSON} from '../lib/bokeh'

const teamsRegExp = /.*\/([a-z]+)_(\d+)_([a-zA-Z ]+)_teams.csv$/

export interface Leagues {
  [key: string]: string[]
}

export async function getLeagues() {
  const prefix = `${AWS_S3_ROOT_KEY}/teams/`
  const leagues: Leagues = {}
  const keys = await listKeys({region: AWS_S3_REGION, bucket: AWS_S3_BUCKET, prefix})
  for (const key of keys) {
    const match = key.match(teamsRegExp)
    if (match) {
      const league = match[1]
      const year = match[2]
      const season_type = match[3]
      if (!(league in leagues)) {
        leagues[league] = []
      }
      leagues[league].push(year)
    }
  }
  for (const league in leagues) {
    const raw_years = leagues[league]
    const years = [...new Set(raw_years)]
    years.sort()
    years.reverse()
    leagues[league] = years
  }
  return leagues
}

export async function getSeasonData(league: string, year: string, seasonType: string) {
  const csvKey = `${AWS_S3_ROOT_KEY}/teams/${league}_${year}_${seasonType}_teams.csv`
  const statsStr = await getObjectString({region: AWS_S3_REGION, bucket: AWS_S3_BUCKET, key: csvKey})
  const stats = parse(statsStr).map(row => {
    return row.slice(0, -3).map( (val: string) => {
      return parseFloat(val) ? parseFloat(val).toFixed(1) : val
    })
  })
  const ratingsKey = `${AWS_S3_ROOT_KEY}/plots/team_ratings_${league}_${year}_${seasonType}.json`
  const ratingsJSONStr = await getObjectString({region: AWS_S3_REGION, bucket: AWS_S3_BUCKET, key: ratingsKey})
  const ratingsJSON = loadJSON(ratingsJSONStr)
  const pacesKey = `${AWS_S3_ROOT_KEY}/plots/team_paces_${league}_${year}_${seasonType}.json`
  const pacesJSONStr = await getObjectString({region: AWS_S3_REGION, bucket: AWS_S3_BUCKET, key: pacesKey})
  const pacesJSON = loadJSON(pacesJSONStr)
  return {
    league,
    year,
    seasonType,
    stats,
    ratingsJSON,
    pacesJSON,
  }
}

interface Latest {
  git_sha: string,
  time: number,
}

export async function getUpdateDate() {
  const key = `${AWS_S3_ROOT_KEY}/latest.yaml`
  const yamlString = await getObjectString({region: AWS_S3_REGION, bucket: AWS_S3_BUCKET, key})
  const latest = load(yamlString) as Latest
  const date = new Date(latest['time'] * 1000)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
