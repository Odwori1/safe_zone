import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'Safe Zone - Mental Health Support',
  description: 'A secure platform for mental health support and community',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  )
}
