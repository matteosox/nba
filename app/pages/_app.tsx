import { AppProps } from 'next/app'
import CssBaseline from '@material-ui/core/CssBaseline'
import { StylesProvider } from '@material-ui/core/styles'
import '../styles/global.css'

export default function App({ Component, pageProps }: AppProps) {
    return (
      <StylesProvider injectFirst>
        <Component {...pageProps}>
          <CssBaseline />
        </Component >
      </StylesProvider>
    )
}
