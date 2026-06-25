import { DM_Sans, Plus_Jakarta_Sans, JetBrains_Mono } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/components/theme-provider'
import { Toaster } from '@/components/ui/sonner'
import { ChunkLoadErrorHandler } from '@/components/chunk-load-error-handler'
import { Providers } from './providers'

export const dynamic = 'force-dynamic';

const dmSans = DM_Sans({ subsets: ['latin'], variable: '--font-sans' })
const jakartaSans = Plus_Jakarta_Sans({ subsets: ['latin'], variable: '--font-display' })
const jetbrainsMono = JetBrains_Mono({ subsets: ['latin'], variable: '--font-mono' })

export const metadata = {
  metadataBase: new URL(process.env.NEXTAUTH_URL || 'https://zenposture.in'),
  title: 'ZenPosture — Fix Your Posture. Transform Your Life. | India\'s #1 Posture Brand',
  description: 'India\'s most trusted posture correction brand. Clinically-designed posture correctors, back support belts & wellness products. 10,000+ happy customers. Free shipping, COD, 30-day guarantee. Starting at ₹499.',
  keywords: 'posture corrector India, back pain relief, shoulder brace, posture belt, postpartum belt, abdominal support belt, desk worker posture, back support belt India, ZenPosture',
  openGraph: {
    title: 'ZenPosture — Fix Your Posture. Transform Your Life.',
    description: '10,000+ Indians trust ZenPosture for posture correction & back pain relief. Premium products from ₹499. Free shipping & COD.',
    images: ['/og-image.png'],
    type: 'website',
    siteName: 'ZenPosture',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'ZenPosture — India\'s #1 Posture Correction Brand',
    description: '10,000+ happy customers. Premium posture correctors from ₹499. Free shipping & COD.',
    images: ['/og-image.png'],
  },
  icons: {
    icon: '/favicon.svg',
    shortcut: '/favicon.svg',
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Meta Pixel */}
        <script dangerouslySetInnerHTML={{ __html: `
          !function(f,b,e,v,n,t,s)
          {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
          n.callMethod.apply(n,arguments):n.queue.push(arguments)};
          if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
          n.queue=[];t=b.createElement(e);t.async=!0;
          t.src=v;s=b.getElementsByTagName(e)[0];
          s.parentNode.insertBefore(t,s)}(window, document,'script',
          'https://connect.facebook.net/en_US/fbevents.js');
          fbq('init', '1483699996385363');
          fbq('track', 'PageView');
        `}} />
        <noscript dangerouslySetInnerHTML={{ __html: `<img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=1483699996385363&ev=PageView&noscript=1"/>` }} />
        {/* Google Ads Tag */}
        <script async src="https://www.googletagmanager.com/gtag/js?id=AW-18224163263" />
        <script dangerouslySetInnerHTML={{ __html: `
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
          gtag('config', 'AW-18224163263');
        `}} />
      </head>
      <body className={`${dmSans.variable} ${jakartaSans.variable} ${jetbrainsMono.variable} font-sans antialiased`}>
        <Providers>
          <ThemeProvider
            attribute="class"
            defaultTheme="light"
            enableSystem={false}
            disableTransitionOnChange
          >
            {children}
            <Toaster />
            <ChunkLoadErrorHandler />
          </ThemeProvider>
        </Providers>
      </body>
    </html>
  )
}
