import { load } from 'js-yaml'
import { getObjectString, listKeys } from '../lib/aws_s3'
import config from '../lib/config'
import { embed } from '@bokeh/bokehjs'
import Papa from 'papaparse'
import { readFileSync } from "fs"

const teamsRegExp = /.*\/([a-z]+)_(\d+)_([a-zA-Z ]+)_teams.csv$/

export interface Leagues {
  [key: string]: string[]
}

export interface StatsRow {
  [key: string]: string | number
}

export type Stats = Array<StatsRow>

export async function getLeagues() {
  const prefix = `${config.awsS3RootKey}/teams/`
  const leagues: Leagues = {}
  const keys = await listKeys({region: config.awsS3Region, bucket: config.awsS3Bucket, prefix})
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
  const csvKey = `${config.awsS3RootKey}/teams/${league}_${year}_${seasonType}_teams.csv`
  const statsStr = await getObjectString({region: config.awsS3Region, bucket: config.awsS3Bucket, key: csvKey})
  const {data: stats}   = Papa.parse(statsStr.trimEnd(), {header: true, dynamicTyping: true})
  const plotKey = `${config.awsS3RootKey}/plots/team_stats_${league}_${year}_${seasonType}.json`
  const plotJSONStr = (
    config.useLocal ? readFileSync(`../data/plots/team_stats_${league}_${year}_${seasonType}.json`).toString()
    : await getObjectString({region: config.awsS3Region, bucket: config.awsS3Bucket, key: plotKey})
  )
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
  const key = `${config.awsS3RootKey}/latest.yaml`
  const yamlString = await getObjectString({region: config.awsS3Region, bucket: config.awsS3Bucket, key})
  const latest = load(yamlString) as Latest
  const date = new Date(latest['time'] * 1000)
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
}
