import type { Metadata } from "next";
import { Montserrat, Raleway, Fira_Code } from "next/font/google";
import { MainNav } from "@/components/layout/nav";
import "./globals.css";

const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
  display: "swap",
});

const raleway = Raleway({
  subsets: ["latin"],
  variable: "--font-raleway",
  display: "swap",
});

const firaCode = Fira_Code({
  subsets: ["latin"],
  variable: "--font-fira-code",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Daily Heavens - Your Personal Astrological Guide",
  description: "Discover your cosmic path with personalized birth charts, compatibility analysis, and daily horoscopes.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={`${montserrat.variable} ${raleway.variable} ${firaCode.variable} font-sans bg-background text-foreground antialiased`}>
        <MainNav />
        <main className="min-h-screen">
          {children}
        </main>
      </body>
    </html>
  );
}
