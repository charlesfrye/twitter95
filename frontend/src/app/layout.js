import { Inter } from "next/font/google";
import "./globals.css";
import ClientLayout from '../components/ClientLayout';

const inter = Inter({ subsets: ["latin"] });

export const metadata = {
  title: "Twitter '95",
  description: "A retro Twitter experience",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div id="app-root">
          <ClientLayout>{children}</ClientLayout>
        </div>
      </body>
    </html>
  );
}
