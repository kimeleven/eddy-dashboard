import statusData from '../public/status.json';

const styles = {
  container: { maxWidth: 1200, margin: '0 auto', padding: '20px' },
  header: { textAlign: 'center' as const, marginBottom: 24 },
  title: { fontSize: 28, fontWeight: 900, color: '#58a6ff', margin: 0 },
  subtitle: { fontSize: 12, color: '#8b949e', marginTop: 4 },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: 16 },
  card: { background: '#161b22', border: '1px solid #30363d', borderRadius: 8, padding: 16 },
  cardTitle: { fontSize: 16, fontWeight: 700, color: '#58a6ff', marginBottom: 12, borderBottom: '1px solid #21262d', paddingBottom: 8 },
  table: { width: '100%', borderCollapse: 'collapse' as const, fontSize: 13 },
  th: { background: '#21262d', color: '#8b949e', textAlign: 'left' as const, padding: '6px 8px', fontWeight: 600 },
  td: { padding: '6px 8px', borderBottom: '1px solid #21262d' },
  badge: (color: string) => ({ display: 'inline-block', padding: '2px 8px', borderRadius: 10, fontSize: 11, fontWeight: 600, background: color, color: '#fff' }),
  logBox: { background: '#0d1117', border: '1px solid #21262d', borderRadius: 6, padding: 10, fontSize: 11, fontFamily: 'monospace', maxHeight: 200, overflow: 'auto', whiteSpace: 'pre-wrap' as const, lineHeight: 1.5, color: '#8b949e' },
  fullWidth: { gridColumn: '1 / -1' },
};

function Badge({ status }: { status: string }) {
  const colors: Record<string, string> = { active: '#238636', scheduled: '#9e6a03', idle: '#30363d', running: '#1f6feb', paused: '#6e4009' };
  return <span style={styles.badge(colors[status] || '#30363d')}>{status}</span>;
}

export default function Dashboard() {
  const data = statusData as any;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Eddy Agent Dashboard</h1>
        <div style={styles.subtitle}>
          Last updated: {data.updatedAt} | Teams: {data.teams?.length || 0} | Total agents: {data.teams?.reduce((s: number, t: any) => s + (t.agents?.length || 0), 0)}
        </div>
      </div>

      <div style={styles.grid}>
        {/* System Info */}
        <div style={styles.card}>
          <div style={styles.cardTitle}>System</div>
          <table style={styles.table}>
            <tbody>
              <tr><td style={styles.td}>Host</td><td style={styles.td}>{data.system?.host}</td></tr>
              <tr><td style={styles.td}>Scheduler</td><td style={styles.td}>{data.system?.scheduler || 'launchd'}</td></tr>
              <tr><td style={styles.td}>Agents</td><td style={styles.td}>{data.system?.launchdAgents || data.system?.cronJobs}개</td></tr>
              <tr><td style={styles.td}>운영시간</td><td style={styles.td}>{data.system?.operatingHours}</td></tr>
              <tr><td style={styles.td}>Model</td><td style={styles.td}>{data.system?.model}</td></tr>
              <tr><td style={styles.td}>Telegram</td><td style={styles.td}>{data.system?.telegram}</td></tr>
            </tbody>
          </table>
        </div>

        {/* Schedule Overview */}
        <div style={styles.card}>
          <div style={styles.cardTitle}>Schedule</div>
          <table style={styles.table}>
            <thead><tr><th style={styles.th}>Team</th><th style={styles.th}>Hours</th><th style={styles.th}>Status</th></tr></thead>
            <tbody>
              {data.teams?.map((team: any) => (
                <tr key={team.name}>
                  <td style={styles.td}>{team.name}</td>
                  <td style={styles.td}>{team.schedule}</td>
                  <td style={styles.td}><Badge status={team.status} /></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Each Team */}
        {data.teams?.map((team: any) => (
          <div key={team.name} style={styles.card}>
            <div style={styles.cardTitle}>{team.icon} {team.name} — {team.description}</div>
            <table style={styles.table}>
              <thead><tr><th style={styles.th}>Agent</th><th style={styles.th}>Role</th><th style={styles.th}>Schedule</th><th style={styles.th}>Last Run</th></tr></thead>
              <tbody>
                {team.agents?.map((agent: any) => (
                  <tr key={agent.name}>
                    <td style={styles.td}><strong>{agent.name}</strong></td>
                    <td style={styles.td}>{agent.role}</td>
                    <td style={styles.td}><code>{agent.schedule || agent.cron}</code></td>
                    <td style={styles.td}>{agent.lastRun || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
            {team.recentLog && (
              <div style={{ marginTop: 12 }}>
                <div style={{ fontSize: 12, color: '#8b949e', marginBottom: 4 }}>Recent Log</div>
                <div style={styles.logBox}>{team.recentLog}</div>
              </div>
            )}
          </div>
        ))}

        {/* Activity Log */}
        <div style={{ ...styles.card, ...styles.fullWidth }}>
          <div style={styles.cardTitle}>Recent Activity</div>
          <div style={styles.logBox}>
            {data.recentActivity?.join('\n') || 'No activity yet'}
          </div>
        </div>
      </div>
    </div>
  );
}
