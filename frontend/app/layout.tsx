import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Resumé Edge — AI Resume Enhancer",
  description: "Get AI-powered, actionable feedback to make your resume land more interviews.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.bunny.net/css?family=satoshi:400,500,700&display=swap"
          rel="stylesheet"
        />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        {children}
      </body>
    </html>
  );
}
