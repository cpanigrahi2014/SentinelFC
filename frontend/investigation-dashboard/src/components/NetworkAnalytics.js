import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Grid, CircularProgress, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Tabs, Tab,
} from '@mui/material';
import { detectFraudRings, getSharedDevices, getCircularTransfers } from '../services/api';
import { useSnackbar } from 'notistack';

function TabPanel({ children, value, index }) {
  return value === index ? <Box sx={{ pt: 2 }}>{children}</Box> : null;
}

export default function NetworkAnalytics() {
  const [tab, setTab] = useState(0);
  const [fraudRings, setFraudRings] = useState([]);
  const [sharedDevices, setSharedDevices] = useState([]);
  const [circularTransfers, setCircularTransfers] = useState([]);
  const [loading, setLoading] = useState(true);
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [rings, devices, circular] = await Promise.all([
          detectFraudRings().catch(() => ({ data: { clusters: [] } })),
          getSharedDevices().catch(() => ({ data: { groups: [] } })),
          getCircularTransfers().catch(() => ({ data: { patterns: [] } })),
        ]);
        setFraudRings(rings.data?.clusters || rings.data || []);
        setSharedDevices(devices.data?.groups || devices.data || []);
        setCircularTransfers(circular.data?.patterns || circular.data || []);
      } catch (err) {
        enqueueSnackbar('Failed to load network data', { variant: 'error' });
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>Network Analytics</Typography>

      <Card>
        <CardContent>
          <Tabs value={tab} onChange={(_, v) => setTab(v)}>
            <Tab label={`Fraud Rings (${fraudRings.length})`} />
            <Tab label={`Shared Devices (${sharedDevices.length})`} />
            <Tab label={`Circular Transfers (${circularTransfers.length})`} />
          </Tabs>

          <TabPanel value={tab} index={0}>
            {fraudRings.length === 0 ? (
              <Typography color="text.secondary">No fraud rings detected</Typography>
            ) : (
              <Grid container spacing={2}>
                {fraudRings.map((ring, i) => (
                  <Grid item xs={12} md={6} key={i}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle1" sx={{ mb: 1 }}>
                        Cluster #{i + 1}
                        <Chip label={`Risk: ${ring.risk_score || 'High'}`} size="small" color="error" sx={{ ml: 1 }} />
                      </Typography>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                        {ring.members?.length || ring.nodes?.length || 0} members
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                        {(ring.members || ring.nodes || []).map((m, j) => (
                          <Chip key={j} label={typeof m === 'string' ? m : m.id || m.customer_id} size="small" variant="outlined" />
                        ))}
                      </Box>
                      {ring.total_amount && (
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          Total: ${ring.total_amount?.toLocaleString()}
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            )}
          </TabPanel>

          <TabPanel value={tab} index={1}>
            {sharedDevices.length === 0 ? (
              <Typography color="text.secondary">No shared device patterns found</Typography>
            ) : (
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Device / IP</TableCell>
                      <TableCell>Accounts</TableCell>
                      <TableCell>Risk</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sharedDevices.map((group, i) => (
                      <TableRow key={i}>
                        <TableCell>{group.device_id || group.ip_address || group.identifier}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {(group.accounts || group.customers || []).map((a, j) => (
                              <Chip key={j} label={a} size="small" variant="outlined" />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip label={group.risk_level || 'medium'} size="small"
                            color={group.risk_level === 'high' ? 'error' : 'warning'} />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </TabPanel>

          <TabPanel value={tab} index={2}>
            {circularTransfers.length === 0 ? (
              <Typography color="text.secondary">No circular transfer patterns detected</Typography>
            ) : (
              <Grid container spacing={2}>
                {circularTransfers.map((pattern, i) => (
                  <Grid item xs={12} key={i}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle1">Pattern #{i + 1}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap', mt: 1 }}>
                        {(pattern.path || pattern.accounts || []).map((node, j, arr) => (
                          <React.Fragment key={j}>
                            <Chip label={node} size="small" />
                            {j < arr.length - 1 && <Typography>→</Typography>}
                          </React.Fragment>
                        ))}
                      </Box>
                      {pattern.total_amount && (
                        <Typography variant="body2" sx={{ mt: 1 }}>
                          Total: ${pattern.total_amount?.toLocaleString()}
                        </Typography>
                      )}
                    </Paper>
                  </Grid>
                ))}
              </Grid>
            )}
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
}
