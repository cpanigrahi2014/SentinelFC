import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Grid, Typography, Chip, CircularProgress,
} from '@mui/material';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import FolderIcon from '@mui/icons-material/Folder';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, Legend,
} from 'recharts';
import { getAlerts, getCases, getServiceStatus } from '../services/api';

const COLORS = ['#d32f2f', '#f57c00', '#fbc02d', '#388e3c', '#1a237e', '#7b1fa2'];

const StatCard = ({ title, value, icon, color }) => (
  <Card>
    <CardContent sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <Box>
        <Typography variant="body2" color="text.secondary">{title}</Typography>
        <Typography variant="h4" sx={{ fontWeight: 700 }}>{value}</Typography>
      </Box>
      <Box sx={{ bgcolor: `${color}15`, borderRadius: 3, p: 1.5, display: 'flex' }}>
        {React.cloneElement(icon, { sx: { fontSize: 32, color } })}
      </Box>
    </CardContent>
  </Card>
);

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [alertsRes, casesRes, statusRes] = await Promise.all([
          getAlerts({ limit: 100 }).catch(() => ({ data: { alerts: [] } })),
          getCases({ limit: 100 }).catch(() => ({ data: { cases: [] } })),
          getServiceStatus().catch(() => ({ data: { services: {} } })),
        ]);

        const alerts = alertsRes.data?.alerts || alertsRes.data || [];
        const cases = casesRes.data?.cases || casesRes.data || [];

        const openAlerts = alerts.filter((a) => a.status === 'new' || a.status === 'open').length;
        const criticalAlerts = alerts.filter((a) => a.severity === 'critical' || a.risk_score >= 90).length;
        const openCases = cases.filter((c) => c.status === 'open' || c.status === 'in_progress').length;
        const resolvedToday = alerts.filter((a) => a.status === 'closed').length;

        // Alert type distribution
        const typeCounts = {};
        alerts.forEach((a) => {
          const t = a.alert_type || a.type || 'unknown';
          typeCounts[t] = (typeCounts[t] || 0) + 1;
        });
        const alertsByType = Object.entries(typeCounts).map(([name, value]) => ({ name, value }));

        // Severity distribution
        const sevCounts = { critical: 0, high: 0, medium: 0, low: 0 };
        alerts.forEach((a) => {
          const s = a.severity || 'medium';
          sevCounts[s] = (sevCounts[s] || 0) + 1;
        });
        const alertsBySeverity = Object.entries(sevCounts).map(([name, value]) => ({ name, value }));

        // Trend data (mock - last 7 days)
        const trend = Array.from({ length: 7 }, (_, i) => ({
          day: `Day ${i + 1}`,
          alerts: Math.floor(Math.random() * 50) + 10,
          cases: Math.floor(Math.random() * 15) + 2,
        }));

        setStats({ openAlerts, criticalAlerts, openCases, resolvedToday, alertsByType, alertsBySeverity, trend, services: statusRes.data });
      } catch (err) {
        console.error('Dashboard fetch error:', err);
        setStats({ openAlerts: 0, criticalAlerts: 0, openCases: 0, resolvedToday: 0, alertsByType: [], alertsBySeverity: [], trend: [], services: {} });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  }

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>Dashboard</Typography>

      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Open Alerts" value={stats.openAlerts} icon={<NotificationsActiveIcon />} color="#f57c00" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Critical Alerts" value={stats.criticalAlerts} icon={<WarningAmberIcon />} color="#d32f2f" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Open Cases" value={stats.openCases} icon={<FolderIcon />} color="#1a237e" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Resolved" value={stats.resolvedToday} icon={<CheckCircleIcon />} color="#388e3c" />
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Alert & Case Trend (7 Days)</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={stats.trend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="day" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="alerts" stroke="#f57c00" strokeWidth={2} />
                  <Line type="monotone" dataKey="cases" stroke="#1a237e" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Alerts by Severity</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie data={stats.alertsBySeverity} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={100} label>
                    {stats.alertsBySeverity.map((_, i) => (
                      <Cell key={i} fill={COLORS[i % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Alerts by Type</Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={stats.alertsByType}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#1a237e" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Service Health</Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {Object.entries(stats.services?.services || {}).map(([name, info]) => (
                  <Chip
                    key={name}
                    label={name.replace(/-/g, ' ')}
                    color={info?.status === 'healthy' ? 'success' : 'error'}
                    variant="outlined"
                    size="small"
                  />
                ))}
                {Object.keys(stats.services?.services || {}).length === 0 && (
                  <Typography variant="body2" color="text.secondary">
                    Connect to API Gateway to view service status
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
