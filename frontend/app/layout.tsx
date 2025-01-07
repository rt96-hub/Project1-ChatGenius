import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { Auth0Provider } from '@/contexts/Auth0Provider'
import { ConnectionProvider } from '@/contexts/ConnectionContext'

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
            {children}
          </ConnectionProvider>
        </Auth0Provider>
      </body>
    </html>
  )
} 