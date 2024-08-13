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
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={msSansSerif.className}>
        <div id="app-root">
          <ClientLayout>{children}</ClientLayout>
        </div>
      </body>
    </html>
  );
}
