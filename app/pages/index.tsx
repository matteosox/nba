import Head from 'next/head'
import Layout from '../components/layout'
import utilStyles from '../styles/utils.module.css'
import { GetStaticProps } from 'next'
import { getUpdateDate, getLeagues, Leagues } from '../lib/leagues'
import { SITE_TITLE } from '../lib/constants'

export default function Home({
  leagues,
  updateDate,
}: {
  leagues: Leagues,
  updateDate: string,
}) {
  return (
    <Layout leagues={leagues} updateDate={updateDate}>
      <Head>
        <title>{SITE_TITLE}</title>
      </Head>
      <section className={utilStyles.headingMd}>
        <h1>NBA Stats & Analysis, powered by Python & NextJS</h1>
        <p>This is an under-construction site hosting NBA stats and analysis.
          Thus far, I've expanded upon <a href="https://cleaningtheglass.com/stats/guide/league_four_factors">Dean Oliver's Four Factors</a>,
          applying <a href="https://en.wikipedia.org/wiki/Bayesian_hierarchical_modeling">Bayesian Hierarchical Modeling</a> using <a href="https://docs.pymc.io/">PyMC3</a> to estimate seven fundamental statistics on a team-by-team basis on both ends of the floor.
          These estimates are opponent, home court, and luck adjusted, with plans for travel, rest, and perhaps even seasonality.
          Finally, I combine these fundamentals to estimate each team's offensive and defensive ratings, which, when combined with pace (also opponent adjusted) on each end of the floor, produce a net margin.
          This brief introduction will have to do for now, but I'll certainly be writing a more complete writeup on my blog at <a href="https://www.mattefay.com">mattefay.com</a>.
          Finally, you can find the code for this site along with the analysis producing these estimates at <a href="https://github.com/matteosox/nba">my github</a>. Cheers!
          </p>
      </section>
    </Layout>
  )
}

export const getStaticProps: GetStaticProps = async () => {
  const leagues = await getLeagues()
  const updateDate = await getUpdateDate()
  return {
    props: {
      leagues,
      updateDate,
    }
  }
}
