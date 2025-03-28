import type { Metadata } from "next";
import { Montserrat, Raleway, Fira_Code } from "next/font/google";
import "./globals.css";

const montserrat = Montserrat({
  subsets: ["latin"],
  variable: "--font-montserrat",
});

const raleway = Raleway({
  subsets: ["latin"],
  variable: "--font-raleway",
});

const firaCode = Fira_Code({
  subsets: ["latin"],
  variable: "--font-fira-code",
});

export const metadata: Metadata = {
  title: "Daily Heavens - Your Personal Astrological Guide",
  description: "Discover your cosmic path with personalized birth charts, compatibility analysis, and daily horoscopes.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${montserrat.variable} ${raleway.variable} ${firaCode.variable} font-sans bg-background text-foreground min-h-screen`}
      >
        {children}
      </body>
    </html>
  );
}
