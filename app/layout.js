// app/layout.js
import { Inter } from 'next/font/google';
import { AuthProvider } from '../contexts/AuthContext';
import ErrorBoundary from '../components/ErrorBoundary';
import './globals.css';

const inter = Inter({ subsets: ['latin'] });

export const metadata = {
  title: 'Avicenna Medicine - Patient Lead Intelligence',
  description: 'AI-powered patient lead analysis and qualification for Avicenna Medicine Integrative & Regenerative Medicine',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ErrorBoundary>
          <AuthProvider>
            {children}
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
