import React from 'react'
import Head from 'next/head'
import Image from 'next/image'
import Link from 'next/link'
import styles from './layout.module.css'
import AppBar from "@material-ui/core/AppBar"
import Toolbar from "@material-ui/core/Toolbar"
import { Leagues } from '../lib/leagues'
import { SITE_TITLE } from '../lib/constants'
import HoverMenu from './menu'

export default function Layout({
  children,
  leagues,
  updateDate,
}: {
  children: React.ReactNode,
  leagues: Leagues,
  updateDate: string,
}) {
  return (
    <div>
      <Head>
        <link rel="icon" href="/basketball.png" />
        <meta
          name="description"
          content="NBA Stats & Analysis, powered by Python & NextJS"
        />
        <meta
          name="viewport"
          content="minimum-scale=1, initial-scale=1, width=device-width"
        />
        <meta
          property="og:site_name"
          content={SITE_TITLE}
        />
      </Head>
      <AppBar className={styles.appBar}>
        <Toolbar className={styles.toolbar}>
          <Link href="/" >
            <a className={styles.toolbarImage}><Image
                src={"/basketball.png"}
                height={45}
                width={45}
            /></a>
          </Link>
          {Object.entries(leagues).map(([league, years]) => (
            <HoverMenu
              className={styles.toolbarMenu}
              key={league}
              name={league}
              items={years.map(year => (
                {name: year, link: `/${league}/${year}`}
              ))}
            />
          ))}
          <div className={styles.grow} />
          <div className={styles.toolbarItem}>
            <p>Updated {updateDate}</p>
          </div>
        </Toolbar>
      </AppBar>
      <main className={styles.main}>{children}</main>
    </div>
  )
}
