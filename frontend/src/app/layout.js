import localFont from "next/font/local";

import "./globals.css";
import ClientLayout from "../components/ClientLayout";

export const viewport = {
  width: "1024",
  initialScale: 1,
};

const msSansSerif = localFont({
  src: "../../public/fonts/ms_sans_serif.woff2",
  display: "swap",
  variable: "--font-ms-sans-serif",
});

export const metadata = {
  title: "Twitter '95",
  description: "What if Twitter was around in 1995?",
  icons: {
    icon: "/logo.png",
  },
  openGraph: {
    title: "Twitter '95",
    description: "What if Twitter was around in 1995?",
    images: [
      {
        url: "/og-image.png",
        width: 1200,
        height: 630,
        alt: "Twitter '95",
      },
    ],
    url: "https://twitter-95.com/",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Twitter '95",
    description: "What if Twitter was around in 1995?",
    images: ["/og-image.png"],
  },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className="h-full w-full">
      <body className={msSansSerif.className}>
        <div className="text-center">
          <ClientLayout>{children}</ClientLayout>
        </div>
      </body>
    </html>
  );
}
