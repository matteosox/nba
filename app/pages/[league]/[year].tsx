import Head from 'next/head'
import { GetStaticProps, GetStaticPaths } from 'next'
import Layout from '../../components/layout'
import MyTable from '../../components/table'
import S3Image from '../../components/s3image'
import { getUpdateDate, getLeagues, getSeasonData, Leagues } from '../../lib/leagues'
import utilStyles from '../../styles/utils.module.css'

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
      ratingsImage: string
      pacesImage: string
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
        <meta property="og:url" content={domain + seasonData.ratingsImage}/>
        <meta name="twitter:card" content="summary_large_image"/>
      </Head>
      <section className={utilStyles.headingMd}>
        <h1>{title} Team Stats</h1>
      </section>
      <div className={utilStyles.centeredImage}>
        <S3Image
          src={seasonData.ratingsImage}
          height={800}
          width={800}
        />
      </div>
      <div className={utilStyles.centeredImage}>
        <S3Image
          src={seasonData.pacesImage}
          height={800}
          width={800}
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
    fallback: false
  }
}

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const leagues = await getLeagues()
  const updateDate = await getUpdateDate()
  const seasonData = await getSeasonData(
    params.league as string,
    params.year as string,
    'Regular Season',
  )
  return {
    props: {
      seasonData,
      updateDate,
      leagues,
    }
  }
}
