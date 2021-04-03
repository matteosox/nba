import { AppProps } from 'next/app'
import CssBaseline from '@material-ui/core/CssBaseline';
import '../styles/global.css'

export default function App({ Component, pageProps }: AppProps) {
    return (
      <Component {...pageProps}>
        <CssBaseline />
      </Component >
    )
}
