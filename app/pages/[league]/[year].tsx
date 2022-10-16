import Head from 'next/head'
import dynamic from 'next/dynamic'
import { GetStaticProps, GetStaticPaths } from 'next'
import { embed } from '@bokeh/bokehjs'
import Layout from '../../components/layout'
import MyTable from '../../components/table'
import { getUpdateDate, getLeagues, getSeasonData, Leagues } from '../../lib/leagues'
import { REVALIDATE_TIME } from '../../lib/constants'
import utilStyles from '../../styles/utils.module.css'

const DynamicBokeh = dynamic(() => import('../../components/bokeh'), {
  ssr: false,
})

export default function Season({
    seasonData,
    leagues,
    updateDate
}: {
    seasonData: {
      league: string,
      year: string,
      seasonType: string,
      stats: Array<Array<number | string>>
      ratingsJSON: embed.JsonItem
      pacesJSON: embed.JsonItem
    },
    leagues: Leagues,
    updateDate: string,
}) {
  const title = `${seasonData.league.toUpperCase()} ${seasonData.year} ${seasonData.seasonType}`
  const domain = "https://nba.mattefay.com"
  return (
    <Layout leagues={leagues} updateDate={updateDate}>
      <Head>
        <title>{title}</title>
        <meta property="og:title" content={title}/>
        <meta property="og:description" content={`${title} Team Stats`}/>
        <meta property="og:url" content={`${domain}/${seasonData.league}/${seasonData.year}`}/>
        <meta name="twitter:card" content="summary_large_image"/>
      </Head>
      <section className={utilStyles.headingMd}>
        <h1>{title} Team Stats</h1>
      </section>
      <div className={utilStyles.centeredImage}>
        <DynamicBokeh
          json={seasonData.ratingsJSON}
          target='team_ratings_plot'
        />
      </div>
      <div className={utilStyles.centeredImage}>
        <DynamicBokeh
          json={seasonData.pacesJSON}
          target='team_paces_plot'
        />
      </div>
      <div>
        <MyTable data={seasonData.stats} />
      </div>
    </Layout>
  )
}

export const getStaticPaths: GetStaticPaths = async () => {
  const leagues = await getLeagues()
  const paths: {params: {league: string, year: string}}[] = []
  Object.entries(leagues).forEach(([league, years]) => {
    years.forEach(year => paths.push({params: {league, year}}))
  })
  return {
    paths,
    fallback: 'blocking'
  }
}

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const league = params.league as string
  const year = params.year as string
  const season_type = 'Regular Season'
  const leagues = await getLeagues()
  if (!(league in leagues) || !(leagues[league].includes(year))) {
    return {notFound: true}
  }
  const updateDate = await getUpdateDate()
  const seasonData = await getSeasonData(league, year, season_type)
  return {
    props: {
      seasonData,
      updateDate,
      leagues,
    },
    revalidate: REVALIDATE_TIME
  }
}
