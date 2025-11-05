import '@/styles/globals.css'
import { useEffect } from 'react';
import { auth } from '@/lib/firebase';

export default function App({ Component, pageProps }) {
  useEffect(() => {
    // Initialize any global auth listeners here if needed
  }, []);

  return <Component {...pageProps} />
}
