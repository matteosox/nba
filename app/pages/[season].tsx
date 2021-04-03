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
    ratings_image: string
    paces_image: string
  }
}) {
  return (
    <Layout>
      <Head>
        <title>{seasonData.season}</title>
      </Head>
      <h1 className={utilStyles.headingXl}>{seasonData.season}</h1>
      <div className={utilStyles.centeredImage}>
        <Image
          src={seasonData.ratings_image}
          height={800}
          width={800}
        />
      </div>
      <div className={utilStyles.centeredImage}>
        <Image
          src={seasonData.paces_image}
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
