import Head from 'next/head'
import Image from 'next/image'
import { GetStaticProps, GetStaticPaths } from 'next'
import Layout from '../components/layout'
import MyTable from '../components/table'
import { getAllSeasons, getSeasonData } from '../lib/seasons'
import utilStyles from '../styles/utils.module.css'

export default function Season({
    seasonData
}: {
    seasonData: {
    season: string
    stats: Array<Array<number | string>>
    ratingsImage: string
    pacesImage: string
  }
}) {
  const title = `NBA ${seasonData.season} Regular Season`
  const domain = "https://nba.mattefay.com"
  return (
    <Layout>
      <Head>
        <title>{title}</title>
        <meta property="og:title" content={title}/>
        <meta property="og:description" content={`NBA ${seasonData.season} Regular Season Team Stats`}/>
        <meta property="og:url" content={domain + seasonData.ratingsImage}/>
        <meta name="twitter:card" content="summary_large_image"/>
      </Head>
      <h1 className={utilStyles.headingXl}>NBA {seasonData.season} Regular Season Team Stats</h1>
      <div className={utilStyles.centeredImage}>
        <Image
          src={seasonData.ratingsImage}
          height={800}
          width={800}
        />
      </div>
      <div className={utilStyles.centeredImage}>
        <Image
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
  const paths = getAllSeasons()
  return {
    paths,
    fallback: false
  }
}

export const getStaticProps: GetStaticProps = async ({ params }) => {
  const seasonData = getSeasonData(params.season as string)
  return {
    props: {
      seasonData
    }
  }
}
