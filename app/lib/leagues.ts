import { load } from 'js-yaml'
import { getObjectString, listKeys } from '../lib/aws_s3'
import { AWS_S3_REGION, AWS_S3_BUCKET, AWS_S3_ROOT_KEY } from '../lib/constants'
import { embed } from '@bokeh/bokehjs'
import Papa from 'papaparse'

const teamsRegExp = /.*\/([a-z]+)_(\d+)_([a-zA-Z ]+)_teams.csv$/

export interface Leagues {
  [key: string]: string[]
}

export interface StatsRow {
  [key: string]: string | number
}

export type Stats = Array<StatsRow>

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
  const {data: stats}   = Papa.parse(statsStr.trimEnd(), {header: true, dynamicTyping: true})
  const plotKey = `${AWS_S3_ROOT_KEY}/plots/team_stats_${league}_${year}_${seasonType}.json`
  const plotJSONStr = await getObjectString({region: AWS_S3_REGION, bucket: AWS_S3_BUCKET, key: plotKey})
  // Load plot JSON locally
  // const plotJSONStr = readFileSync(`../data/plots/team_stats_${league}_${year}_${seasonType}.json`).toString()
  const plotJSON = JSON.parse(plotJSONStr) as embed.JsonItem  
  return {
    league,
    year,
    seasonType,
    stats,
    plotJSON,
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
