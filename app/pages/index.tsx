import Head from 'next/head'
import Link from 'next/link'
import Layout, { siteTitle } from '../components/layout'
import utilStyles from '../styles/utils.module.css'
import { GetStaticProps } from 'next'
import { getAllSeasons } from '../lib/seasons'

export default function Home({
  seasons
}: {
  seasons: {
    params: {
      season: string
    }
  }[]
}) {
  return (
    <Layout home>
      <Head>
        <title>{siteTitle}</title>
      </Head>
      <section className={utilStyles.headingMd}>
        <p>NBA Stats & Analysis, powered by Python & NextJS</p>
      </section>
      <section className={`${utilStyles.headingMd} ${utilStyles.padding1px}`}>
        <h2 className={utilStyles.headingLg}>Seasons</h2>
        <ul className={utilStyles.list}>
          {seasons.map(({ params }) => (
            <li className={utilStyles.listItem} key={params.season}>
              <Link href={`/${params.season}`}>
                <a>{params.season}</a>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </Layout>
  )
}

export const getStaticProps: GetStaticProps = async () => {
  const seasons = getAllSeasons()
  return {
    props: {
      seasons
    }
  }
}
