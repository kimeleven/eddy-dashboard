export const metadata = { title: 'Eddy Dashboard', description: 'Agent System Monitor' };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ko">
      <body style={{ margin: 0, fontFamily: '-apple-system, sans-serif', background: '#0d1117', color: '#e6edf3' }}>
        {children}
      </body>
    </html>
  );
}
