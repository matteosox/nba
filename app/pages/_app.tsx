import { AppProps } from 'next/app'
import { Analytics } from '@vercel/analytics/react'
import CssBaseline from '@material-ui/core/CssBaseline'
import { StylesProvider } from '@material-ui/core/styles'
import '../styles/global.css'
import '../styles/tabulator.scss'

export default function App({ Component, pageProps }: AppProps) {
    return (
      <StylesProvider injectFirst>
        <Component {...pageProps}>
          <CssBaseline />
        </Component >
        <Analytics />
      </StylesProvider>
    )
}
