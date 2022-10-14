import Head from 'next/head'
import dynamic from 'next/dynamic'
import { GetStaticProps, GetStaticPaths } from 'next'
import Layout from '../../components/layout'
import MyTable from '../../components/table'
import S3Image from '../../components/s3image'
import { getUpdateDate, getLeagues, getSeasonData, Leagues } from '../../lib/leagues'
import { loadJSON } from '../../lib/bokeh'
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
      ratingsImage: string
      pacesImage: string
    },
    leagues: Leagues,
    updateDate: string,
}) {
  const title = `${seasonData.league.toUpperCase()} ${seasonData.year} ${seasonData.seasonType}`
  const domain = "https://nba.mattefay.com"
  const json_str = '{"target_id": null, "root_id": "3135", "doc": {"defs": [], "roots": {"references": [{"attributes": {"below": [{"id": "3144"}], "center": [{"id": "3147"}, {"id": "3151"}], "left": [{"id": "3148"}], "renderers": [{"id": "3169"}], "title": {"id": "3294"}, "toolbar": {"id": "3159"}, "x_range": {"id": "3136"}, "x_scale": {"id": "3140"}, "y_range": {"id": "3138"}, "y_scale": {"id": "3142"}}, "id": "3135", "subtype": "Figure", "type": "Plot"}, {"attributes": {"source": {"id": "3166"}}, "id": "3170", "type": "CDSView"}, {"attributes": {}, "id": "3140", "type": "LinearScale"}, {"attributes": {}, "id": "3156", "type": "ResetTool"}, {"attributes": {}, "id": "3157", "type": "HelpTool"}, {"attributes": {}, "id": "3303", "type": "UnionRenderers"}, {"attributes": {}, "id": "3136", "type": "DataRange1d"}, {"attributes": {}, "id": "3142", "type": "LinearScale"}, {"attributes": {"axis": {"id": "3148"}, "dimension": 1, "ticker": null}, "id": "3151", "type": "Grid"}, {"attributes": {"overlay": {"id": "3158"}}, "id": "3154", "type": "BoxZoomTool"}, {"attributes": {}, "id": "3145", "type": "BasicTicker"}, {"attributes": {"active_multi": null, "tools": [{"id": "3152"}, {"id": "3153"}, {"id": "3154"}, {"id": "3155"}, {"id": "3156"}, {"id": "3157"}]}, "id": "3159", "type": "Toolbar"}, {"attributes": {"formatter": {"id": "3295"}, "major_label_policy": {"id": "3296"}, "ticker": {"id": "3149"}}, "id": "3148", "type": "LinearAxis"}, {"attributes": {"fill_alpha": {"value": 0.1}, "fill_color": {"value": "#1f77b4"}, "line_alpha": {"value": 0.1}, "line_color": {"value": "#1f77b4"}, "x": {"field": "x"}, "y": {"field": "y"}}, "id": "3168", "type": "Circle"}, {"attributes": {"data_source": {"id": "3166"}, "glyph": {"id": "3167"}, "hover_glyph": null, "muted_glyph": null, "nonselection_glyph": {"id": "3168"}, "view": {"id": "3170"}}, "id": "3169", "type": "GlyphRenderer"}, {"attributes": {}, "id": "3298", "type": "BasicTickFormatter"}, {"attributes": {"formatter": {"id": "3298"}, "major_label_policy": {"id": "3299"}, "ticker": {"id": "3145"}}, "id": "3144", "type": "LinearAxis"}, {"attributes": {}, "id": "3149", "type": "BasicTicker"}, {"attributes": {}, "id": "3299", "type": "AllLabels"}, {"attributes": {}, "id": "3152", "type": "PanTool"}, {"attributes": {}, "id": "3155", "type": "SaveTool"}, {"attributes": {}, "id": "3138", "type": "DataRange1d"}, {"attributes": {}, "id": "3294", "type": "Title"}, {"attributes": {"fill_color": {"value": "#1f77b4"}, "line_color": {"value": "#1f77b4"}, "x": {"field": "x"}, "y": {"field": "y"}}, "id": "3167", "type": "Circle"}, {"attributes": {}, "id": "3153", "type": "WheelZoomTool"}, {"attributes": {"data": {"x": [1, 2, 3], "y": [0, 1, 0]}, "selected": {"id": "3302"}, "selection_policy": {"id": "3303"}}, "id": "3166", "type": "ColumnDataSource"}, {"attributes": {}, "id": "3295", "type": "BasicTickFormatter"}, {"attributes": {}, "id": "3302", "type": "Selection"}, {"attributes": {"bottom_units": "screen", "fill_alpha": 0.5, "fill_color": "lightgrey", "left_units": "screen", "level": "overlay", "line_alpha": 1.0, "line_color": "black", "line_dash": [4, 4], "line_width": 2, "right_units": "screen", "syncable": false, "top_units": "screen"}, "id": "3158", "type": "BoxAnnotation"}, {"attributes": {}, "id": "3296", "type": "AllLabels"}, {"attributes": {"axis": {"id": "3144"}, "ticker": null}, "id": "3147", "type": "Grid"}], "root_ids": ["3135"]}, "title": "", "version": "2.3.3"}}'
  const json_item = loadJSON(json_str)
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
      <DynamicBokeh
        json={json_item}
        target='testy'
      />
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
