import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Auth0Provider } from '@/contexts/Auth0Provider'
import { ConnectionProvider } from '@/contexts/ConnectionContext'
import { AIProvider } from '@/contexts/AIContext'
import { Toaster } from 'react-hot-toast'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ChatGenius',
  description: 'A modern real-time chat application',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <Auth0Provider>
          <ConnectionProvider>
            <AIProvider>
              {children}
            </AIProvider>
          </ConnectionProvider>
        </Auth0Provider>
        <Toaster position="top-right" />
      </body>
    </html>
  )
} 