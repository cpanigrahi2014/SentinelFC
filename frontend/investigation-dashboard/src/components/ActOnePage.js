import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Paper, Tabs, Tab, Grid, Card, CardContent, Chip, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Alert, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, MenuItem, Select, FormControl, InputLabel,
  Divider, IconButton, Tooltip, Accordion, AccordionSummary,
  AccordionDetails, List, ListItem, ListItemIcon, ListItemText,
} from '@mui/material';
import WorkIcon from '@mui/icons-material/Work';
import DashboardIcon from '@mui/icons-material/Dashboard';
import GavelIcon from '@mui/icons-material/Gavel';
import SearchIcon from '@mui/icons-material/Search';
import PersonIcon from '@mui/icons-material/Person';
import DescriptionIcon from '@mui/icons-material/Description';
import TimelineIcon from '@mui/icons-material/Timeline';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import RefreshIcon from '@mui/icons-material/Refresh';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import InfoIcon from '@mui/icons-material/Info';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import StorageIcon from '@mui/icons-material/Storage';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import TuneIcon from '@mui/icons-material/Tune';
import SecurityIcon from '@mui/icons-material/Security';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AssignmentIcon from '@mui/icons-material/Assignment';
import {
  getActoneDashboard, getActoneCases, actoneTriage,
  actoneScenarioAml, actoneScenarioFraud, actoneScenarioSurveillance, actoneScenarioSpoofingLayering, actoneScenarioWashTrading, actoneScenarioPumpAndDump, actoneScenarioMarkingTheClose, actoneScenarioQuoteStuffing, actoneScenarioInsiderBeforeNews, actoneScenarioInsiderConnectedAccounts, actoneScenarioInsiderInfoLeakage, actoneScenarioCoordinatedTrading, actoneScenarioCircularTrading, actoneScenarioCrossMarketManipulation, actoneScenarioMomentumIgnition, actoneScenarioLatencyArbitrage, actoneScenarioOrderBookImbalance, actoneScenarioTraderBehaviorDeviation, actoneScenarioRogueTrader, actoneScenarioUnusualProfitability, actoneScenarioEquityOptionsManipulation, actoneScenarioFxManipulation, actoneScenarioCommodityManipulation, actoneScenarioRegulatoryCompliance, actoneScenarioMissingData, actoneScenarioDuplicateTrades, actoneScenarioTimeSyncIssues, actoneScenarioRuleEngineTesting,
  getActoneCustomer360, getActoneStateMachine, getActoneAudit, getActoneInfo,
} from '../services/api';

// ═══════════════════ Helper Components ═══════════════════

const priorityColor = (p) => {
  const map = { critical: 'error', high: 'warning', medium: 'info', low: 'success' };
  return map[p] || 'default';
};

const statusColor = (s) => {
  const map = {
    new: 'default', triaged: 'info', assigned: 'info',
    in_investigation: 'warning', evidence_gathering: 'warning',
    pending_review: 'info', escalated: 'error', pending_approval: 'warning',
    sar_drafting: 'info', sar_filed: 'success',
    account_frozen: 'error', customer_contacted: 'warning',
    closed_no_action: 'default', closed_sar_filed: 'success',
    closed_false_positive: 'default', closed_referred: 'success', reopened: 'warning',
  };
  return map[s] || 'default';
};

const caseTypeIcon = (t) => {
  const map = { aml: <GavelIcon fontSize="small" />, fraud: <SecurityIcon fontSize="small" />, surveillance: <TrendingUpIcon fontSize="small" /> };
  return map[t] || <WorkIcon fontSize="small" />;
};

const StatCard = ({ title, value, color, subtitle }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Typography variant="body2" color="text.secondary" gutterBottom>{title}</Typography>
      <Typography variant="h4" fontWeight={700} sx={{ fontSize: { xs: '1.5rem', md: '2.125rem' } }} color={color || 'text.primary'}>{value}</Typography>
      {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
    </CardContent>
  </Card>
);

// ═══════════════════ KPI Dashboard Tab ═══════════════════

function KPIDashboardTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try { const res = await getActoneDashboard(); setData(res.data); }
    catch (e) { console.error('Failed to load ActOne dashboard:', e); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Box textAlign="center" py={4}><CircularProgress /></Box>;
  if (!data) return <Alert severity="info">Click refresh to load dashboard</Alert>;

  const sd = data.status_distribution || {};
  const pd = data.priority_distribution || {};
  const td = data.case_type_distribution || {};
  const sla = data.sla_metrics || {};
  const sar = data.sar_metrics || {};

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>KPI Dashboard</Typography>
        <Button startIcon={<RefreshIcon />} onClick={load} variant="outlined" size="small">Refresh</Button>
      </Box>

      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} md={3}><StatCard title="Total Cases" value={data.total_cases} color="primary.main" /></Grid>
        <Grid item xs={6} md={3}><StatCard title="SLA Breach Rate" value={`${sla.breach_rate_pct || 0}%`} color="error.main" /></Grid>
        <Grid item xs={6} md={3}><StatCard title="SARs Filed" value={sar.total_filed || 0} color="success.main" /></Grid>
        <Grid item xs={6} md={3}><StatCard title="Avg Resolution" value={`${data.avg_resolution_hours || 0}h`} color="info.main" /></Grid>
      </Grid>

      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>Status Distribution</Typography>
              {Object.entries(sd).map(([k, v]) => (
                <Box key={k} display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
                  <Chip label={k.replace(/_/g, ' ')} size="small" color={statusColor(k)} variant="outlined" />
                  <Typography fontWeight={600}>{v}</Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>Priority Distribution</Typography>
              {Object.entries(pd).map(([k, v]) => (
                <Box key={k} display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
                  <Chip label={k} size="small" color={priorityColor(k)} />
                  <Typography fontWeight={600}>{v}</Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="subtitle2" gutterBottom fontWeight={600}>Case Type Distribution</Typography>
              {Object.entries(td).map(([k, v]) => (
                <Box key={k} display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
                  <Box display="flex" alignItems="center" gap={1}>{caseTypeIcon(k)}<Typography variant="body2">{k.toUpperCase()}</Typography></Box>
                  <Typography fontWeight={600}>{v}</Typography>
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Card>
        <CardContent>
          <Typography variant="subtitle2" gutterBottom fontWeight={600}>Investigator Workload</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Investigator</TableCell>
                  <TableCell align="center">Active Cases</TableCell>
                  <TableCell align="center">SLA Breaches</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {(data.investigator_workload || []).map((inv) => (
                  <TableRow key={inv.investigator}>
                    <TableCell>{inv.investigator}</TableCell>
                    <TableCell align="center">{inv.active_cases}</TableCell>
                    <TableCell align="center">
                      <Chip label={inv.sla_breaches} size="small" color={inv.sla_breaches > 0 ? 'error' : 'success'} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
}

// ═══════════════════ Alert Triage Tab ═══════════════════

function AlertTriageTab() {
  const [open, setOpen] = useState(false);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    alert_id: 'ALT-NEW-001', alert_type: 'aml', amount: 75000,
    customer_risk_score: 0.6, is_pep: false, sanctions_flag: false,
  });

  const handleTriage = async () => {
    setLoading(true);
    try { const res = await actoneTriage(form); setResult(res.data); }
    catch (e) { console.error('Triage failed:', e); }
    setLoading(false);
    setOpen(false);
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>Alert Triage & Prioritization</Typography>
        <Button startIcon={<PlayArrowIcon />} onClick={() => setOpen(true)} variant="contained" size="small">Triage Alert</Button>
      </Box>

      <Alert severity="info" sx={{ mb: 2 }}>
        <strong>Priority Scoring:</strong> Composite score = amount_risk (30%) + customer_risk (30%) + PEP_flag (20%) + sanctions_flag (20%).
        Critical ≥0.8, High ≥0.6, Medium ≥0.4, Low &lt;0.4.
      </Alert>

      <Alert severity="warning" sx={{ mb: 2 }}>
        <strong>SLA Targets:</strong> Critical: 4h investigation / 24h resolution • High: 24h / 72h • Medium: 72h / 168h • Low: 168h / 720h
      </Alert>

      {result && (
        <Card sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>Triage Result</Typography>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Typography variant="body2" color="text.secondary">Case ID</Typography>
                <Typography fontWeight={600}>{result.case_id}</Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="body2" color="text.secondary">Priority</Typography>
                <Chip label={result.priority} color={priorityColor(result.priority)} size="small" />
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="body2" color="text.secondary">Score</Typography>
                <Typography fontWeight={600}>{result.priority_score}</Typography>
              </Grid>
              <Grid item xs={6} md={3}>
                <Typography variant="body2" color="text.secondary">SLA (Investigate/Resolve)</Typography>
                <Typography fontWeight={600}>{result.sla?.investigation_hours}h / {result.sla?.resolution_hours}h</Typography>
              </Grid>
            </Grid>
            <Divider sx={{ my: 1 }} />
            <Typography variant="body2" color="text.secondary" gutterBottom>Timeline</Typography>
            {(result.timeline || []).map((ev, i) => (
              <Box key={i} display="flex" gap={1} alignItems="center" py={0.3}>
                <Chip label={ev.event} size="small" variant="outlined" />
                <Typography variant="caption">{ev.actor}</Typography>
              </Box>
            ))}
          </CardContent>
        </Card>
      )}

      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Triage New Alert</DialogTitle>
        <DialogContent>
          <Box display="flex" flexDirection="column" gap={2} mt={1}>
            <TextField label="Alert ID" value={form.alert_id} onChange={(e) => setForm({ ...form, alert_id: e.target.value })} size="small" />
            <FormControl size="small">
              <InputLabel>Alert Type</InputLabel>
              <Select label="Alert Type" value={form.alert_type} onChange={(e) => setForm({ ...form, alert_type: e.target.value })}>
                <MenuItem value="aml">AML</MenuItem>
                <MenuItem value="fraud">Fraud</MenuItem>
                <MenuItem value="surveillance">Surveillance</MenuItem>
              </Select>
            </FormControl>
            <TextField label="Transaction Amount" type="number" value={form.amount} onChange={(e) => setForm({ ...form, amount: Number(e.target.value) })} size="small" />
            <TextField label="Customer Risk Score (0-1)" type="number" inputProps={{ step: 0.1, min: 0, max: 1 }} value={form.customer_risk_score} onChange={(e) => setForm({ ...form, customer_risk_score: Number(e.target.value) })} size="small" />
            <FormControl size="small">
              <InputLabel>PEP Status</InputLabel>
              <Select label="PEP Status" value={form.is_pep} onChange={(e) => setForm({ ...form, is_pep: e.target.value })}>
                <MenuItem value={false}>No</MenuItem>
                <MenuItem value={true}>Yes</MenuItem>
              </Select>
            </FormControl>
            <FormControl size="small">
              <InputLabel>Sanctions Flag</InputLabel>
              <Select label="Sanctions Flag" value={form.sanctions_flag} onChange={(e) => setForm({ ...form, sanctions_flag: e.target.value })}>
                <MenuItem value={false}>No</MenuItem>
                <MenuItem value={true}>Yes</MenuItem>
              </Select>
            </FormControl>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={handleTriage} variant="contained" disabled={loading}>
            {loading ? <CircularProgress size={20} /> : 'Triage'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

// ═══════════════════ Cases Tab ═══════════════════

function CasesTab() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try { const res = await getActoneCases(); setCases(res.data.cases || []); }
    catch (e) { console.error('Failed to load cases:', e); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Box textAlign="center" py={4}><CircularProgress /></Box>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>Investigation Cases</Typography>
        <Button startIcon={<RefreshIcon />} onClick={load} variant="outlined" size="small">Refresh</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Case ID</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Priority</TableCell>
              <TableCell>Assignee</TableCell>
              <TableCell>Title</TableCell>
              <TableCell>Created</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {cases.map((c) => (
              <TableRow key={c.case_id} hover>
                <TableCell><Typography fontWeight={600} variant="body2">{c.case_id}</Typography></TableCell>
                <TableCell><Box display="flex" alignItems="center" gap={0.5}>{caseTypeIcon(c.case_type)}<Typography variant="body2">{c.case_type.toUpperCase()}</Typography></Box></TableCell>
                <TableCell><Chip label={c.status.replace(/_/g, ' ')} size="small" color={statusColor(c.status)} /></TableCell>
                <TableCell><Chip label={c.priority} size="small" color={priorityColor(c.priority)} /></TableCell>
                <TableCell>{c.assignee || '—'}</TableCell>
                <TableCell><Typography variant="body2" sx={{ maxWidth: { xs: 150, sm: 300 }, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{c.title}</Typography></TableCell>
                <TableCell><Typography variant="caption">{new Date(c.created_at).toLocaleDateString()}</Typography></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

// ═══════════════════ Customer 360 Tab ═══════════════════

function Customer360Tab() {
  const [customerId, setCustomerId] = useState('CUST-001');
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = async () => {
    setLoading(true);
    try { const res = await getActoneCustomer360(customerId); setData(res.data); }
    catch (e) { console.error('Failed to load Customer 360:', e); }
    setLoading(false);
  };

  return (
    <Box>
      <Box display="flex" gap={2} alignItems="center" flexWrap="wrap" mb={2}>
        <Typography variant="h6" fontWeight={600}>Customer 360 View</Typography>
        <TextField label="Customer ID" size="small" value={customerId} onChange={(e) => setCustomerId(e.target.value)} />
        <Button startIcon={<SearchIcon />} onClick={load} variant="contained" size="small" disabled={loading}>
          {loading ? <CircularProgress size={20} /> : 'Lookup'}
        </Button>
      </Box>

      {!data && <Alert severity="info">Enter a customer ID and click Lookup to view customer profile.</Alert>}

      {data && (
        <Grid container spacing={2}>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  <PersonIcon sx={{ verticalAlign: 'middle', mr: 1 }} />Profile
                </Typography>
                <Grid container spacing={1}>
                  {[
                    ['Customer ID', data.customer_id],
                    ['Name', data.customer_name],
                    ['Type', data.customer_type],
                    ['KYC Status', data.kyc_status],
                    ['Last KYC Review', data.last_kyc_review],
                  ].map(([label, val]) => (
                    <React.Fragment key={label}>
                      <Grid item xs={5}><Typography variant="body2" color="text.secondary">{label}</Typography></Grid>
                      <Grid item xs={7}><Typography variant="body2" fontWeight={600}>{val}</Typography></Grid>
                    </React.Fragment>
                  ))}
                </Grid>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>Risk Profile</Typography>
                <Grid container spacing={1}>
                  <Grid item xs={6}><StatCard title="Risk Score" value={data.risk_score} color={data.risk_score >= 0.7 ? 'error.main' : 'warning.main'} /></Grid>
                  <Grid item xs={6}><StatCard title="Total Alerts" value={data.total_alerts} color="warning.main" /></Grid>
                  <Grid item xs={6}><StatCard title="Total Cases" value={data.total_cases} color="info.main" /></Grid>
                  <Grid item xs={6}><StatCard title="Sanctions Hits" value={data.sanctions_hits} color={data.sanctions_hits > 0 ? 'error.main' : 'success.main'} /></Grid>
                </Grid>
                <Box mt={1}>
                  <Chip label={data.pep_status ? 'PEP: YES' : 'PEP: NO'} size="small" color={data.pep_status ? 'error' : 'success'} />
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>Accounts</Typography>
                <TableContainer>
                  <Table size="small">
                    <TableHead><TableRow><TableCell>Account</TableCell><TableCell>Type</TableCell><TableCell align="right">Balance</TableCell><TableCell>Status</TableCell></TableRow></TableHead>
                    <TableBody>
                      {(data.accounts || []).map((a) => (
                        <TableRow key={a.account_id}>
                          <TableCell>{a.account_id}</TableCell><TableCell>{a.type}</TableCell>
                          <TableCell align="right">${a.balance?.toLocaleString()}</TableCell>
                          <TableCell><Chip label={a.status} size="small" color="success" /></TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>Recent Alerts</Typography>
                <List dense>
                  {(data.recent_alerts || []).map((al) => (
                    <ListItem key={al.alert_id}>
                      <ListItemIcon><WarningAmberIcon color="warning" /></ListItemIcon>
                      <ListItemText primary={`${al.alert_id} — ${al.type.replace(/_/g, ' ')}`} secondary={`$${al.amount?.toLocaleString()} · ${al.date}`} />
                    </ListItem>
                  ))}
                </List>
                <Divider sx={{ my: 1 }} />
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Related Parties</Typography>
                <List dense>
                  {(data.related_parties || []).map((rp, i) => (
                    <ListItem key={i}>
                      <ListItemIcon><PersonIcon /></ListItemIcon>
                      <ListItemText primary={rp.name} secondary={`${rp.relationship.replace(/_/g, ' ')} · Risk: ${rp.risk_level}`} />
                    </ListItem>
                  ))}
                </List>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}
    </Box>
  );
}

// ═══════════════════ Scenarios Tab ═══════════════════

function ScenariosTab() {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});

  const runScenario = async (key, fn) => {
    setLoading((p) => ({ ...p, [key]: true }));
    try { const res = await fn(); setResults((p) => ({ ...p, [key]: res.data })); }
    catch (e) { console.error(`Scenario ${key} failed:`, e); }
    setLoading((p) => ({ ...p, [key]: false }));
  };

  const scenarios = [
    { key: 'aml', label: 'AML Alert Investigation', icon: <GavelIcon />, fn: actoneScenarioAml,
      desc: 'Suspicious transaction → triage → assign → investigate → evidence → Customer 360 → SAR draft → SAR filed → closed' },
    { key: 'fraud', label: 'Fraud Case — Account Takeover', icon: <SecurityIcon />, fn: actoneScenarioFraud,
      desc: 'Fraud alert → triage → assign → freeze account → contact customer → evidence → close/refer' },
    { key: 'surveillance', label: 'Trading Surveillance', icon: <TrendingUpIcon />, fn: actoneScenarioSurveillance,
      desc: 'Suspicious trade → triage → assign → communication review → escalate → approval → regulatory referral' },
    { key: 'spoofing', label: 'Spoofing / Layering Detection', icon: <TrendingUpIcon />, fn: actoneScenarioSpoofingLayering,
      desc: 'Pattern detection (order-to-trade ratio, cancel time, BBO distance) → order book reconstruction → trader profiling (algo vs human) → market impact → edge cases (partial fills) → compliance → SEC/FINRA referral' },
    { key: 'washTrading', label: 'Wash Trading Detection', icon: <TrendingUpIcon />, fn: actoneScenarioWashTrading,
      desc: 'Self-trade detection (same beneficial owner, same IP/device, circular trades) → ownership analysis → IP/device correlation → circular chain reconstruction → volume impact → compliance → SEC/FINRA referral' },
    { key: 'pumpAndDump', label: 'Pump and Dump Detection', icon: <TrendingUpIcon />, fn: actoneScenarioPumpAndDump,
      desc: 'Price/volume anomaly → social sentiment analysis (bots, fake press releases) → accumulation pattern → insider selling correlation (late Form 4) → dump & collapse → compliance → SEC/FINRA referral' },
    { key: 'markingTheClose', label: 'Marking the Close', icon: <TrendingUpIcon />, fn: actoneScenarioMarkingTheClose,
      desc: 'Closing window anomaly (large trades in last 5–10 min) → VWAP deviation analysis → trade pattern reconstruction → portfolio NAV impact → historical quarter-end pattern → compliance → SEC/FINRA referral' },
    { key: 'quoteStuffing', label: 'Quote Stuffing Detection', icon: <TrendingUpIcon />, fn: actoneScenarioQuoteStuffing,
      desc: 'Message rate anomaly (thousands of orders/sec) → exchange latency impact → cancellation ratio analysis (99%+ cancel, sub-ms lifespan) → stale NBBO exploitation → historical pattern → compliance → SEC/FINRA referral' },
    { key: 'insiderBeforeNews', label: 'Insider: Trading Before Material News', icon: <SecurityIcon />, fn: actoneScenarioInsiderBeforeNews,
      desc: 'Trade timestamp vs news release correlation → profit-after-event (options leverage) → MNPI access verification → trading pattern anomaly (zero prior history) → communication surveillance → compliance → SEC/DOJ referral' },
    { key: 'insiderConnected', label: 'Insider: Connected Accounts', icon: <SecurityIcon />, fn: actoneScenarioInsiderConnectedAccounts,
      desc: 'Shared address/phone/device scan → trading pattern correlation (tippee network) → profit-after-event → communication link analysis → insider MNPI access confirmation → compliance → SEC/DOJ referral' },
    { key: 'insiderInfoLeakage', label: 'Insider: Information Leakage', icon: <SecurityIcon />, fn: actoneScenarioInsiderInfoLeakage,
      desc: 'Small repeated buys detection (gradual accumulation) → pattern clustering (lot size growth, timing, broker splitting) → news event correlation → profit analysis → information source investigation → compliance → SEC/FINRA referral' },
    { key: 'coordinatedTrading', label: 'Coordinated Trading Ring', icon: <TrendingUpIcon />, fn: actoneScenarioCoordinatedTrading,
      desc: 'Time synchronization detection (6 accounts within 1.96 sec) → strategy execution analysis (same algo fingerprint) → coordinated exit detection → network relationship mapping → market impact → compliance → SEC/FINRA/DOJ referral' },
    { key: 'circularTrading', label: 'Circular Trading (A→B→C→A)', icon: <TrendingUpIcon />, fn: actoneScenarioCircularTrading,
      desc: 'Trade chain graph detection (circular loop) → ownership change verification (net zero) → price inflation measurement → beneficial ownership mapping (common UBO) → retail harm → compliance → SEC/FINRA/DOJ referral' },
    { key: 'crossMarketManipulation', label: 'Cross-Market Manipulation', icon: <TrendingUpIcon />, fn: actoneScenarioCrossMarketManipulation,
      desc: 'Futures/equity correlation check (beta divergence) → price movement linkage → derivative preloading detection → manipulation profit calculation → cross-exchange review → compliance → SEC/CFTC/DOJ referral' },
    { key: 'momentumIgnition', label: 'Momentum Ignition', icon: <TrendingUpIcon />, fn: actoneScenarioMomentumIgnition,
      desc: 'Burst trade detection (aggressive orders → price spike) → momentum cascade (stop-losses + algo triggers + retail FOMO) → profit exit at peak → price reversion confirmation (99%+) → historical pattern → compliance → SEC/FINRA referral' },
    { key: 'latencyArbitrage', label: 'Latency Arbitrage', icon: <SecurityIcon />, fn: actoneScenarioLatencyArbitrage,
      desc: 'Faster execution vs market data lag (40µs vs 900µs) → stale quote exploitation mapping → victim impact (MM + institutional + retail) → infrastructure investigation (co-lo, microwave) → compliance → SEC/FINRA referral' },
    { key: 'orderBookImbalance', label: 'Order Book Imbalance Exploitation', icon: <SecurityIcon />, fn: actoneScenarioOrderBookImbalance,
      desc: 'Sudden imbalance creation (phantom bid/ask wall) → reversal detection (mass cancel + opposite execution) → intent analysis (0% fill rate) → victim impact → 30-day pattern history → compliance → SEC/FINRA referral' },
    { key: 'traderBehaviorDeviation', label: 'Trader Behavior Deviation', icon: <TrendingUpIcon />, fn: actoneScenarioTraderBehaviorDeviation,
      desc: 'New instrument detection (0% historical overlap) → sudden volume increase (3.11x, Z-score 4.8) → trading time shift (62% outside normal hours) → AI behavioral clustering (94.2% dissimilar, anomaly 96/100) → event correlation → compliance → SEC/FINRA referral' },
    { key: 'rogueTrader', label: 'Rogue Trader Detection', icon: <WarningAmberIcon />, fn: actoneScenarioRogueTrader,
      desc: 'Limit breach detection (5.72x authorized, 7 breaches) → overnight exposure spike ($8.2M→$97M) → unauthorized instruments (92% off-mandate) → control circumvention (account splitting, DMA bypass) → loss concealment ($21.6M) → compliance → SEC/FINRA/DOJ referral' },
    { key: 'unusualProfitability', label: 'Unusual Profitability Detection', icon: <TrendingUpIcon />, fn: actoneScenarioUnusualProfitability,
      desc: 'Sharpe ratio spike (6.84 vs 1.35 peer, 4.06σ) → win-rate anomaly (94.2% vs 54.8% peer, 100% on event days) → profit decomposition (7.8x peer) → pre-announcement pattern → information source investigation → statistical impossibility (<10^-18) → SEC/FINRA/DOJ referral' },
    { key: 'equityOptionsManipulation', label: 'Equity ↔ Options Manipulation', icon: <SecurityIcon />, fn: actoneScenarioEquityOptionsManipulation,
      desc: 'Cross-asset position buildup (equity + OTM calls, 6.2x leverage) → stock price manipulation (+6.6%, 28% volume) → options profit amplification (224%, $9.4M) → closing price manipulation → cross-asset coordination → compliance → SEC/CBOE/FINRA referral' },
    { key: 'fxManipulation', label: 'FX Benchmark Manipulation', icon: <SecurityIcon />, fn: actoneScenarioFxManipulation,
      desc: 'Benchmark rate manipulation (WM/Reuters fix, 4.2 pips) → pre-hedging/front-running ($2.1B client orders, $6.2M harm) → chat room collusion (3 banks, 287 messages) → statistical analysis (91.1% success) → multi-jurisdictional referral (CFTC/FCA/DOJ)' },
    { key: 'commodityManipulation', label: 'Commodity Manipulation', icon: <WarningAmberIcon />, fn: actoneScenarioCommodityManipulation,
      desc: 'Physical hoarding (68% warehouse, 142K MT) → queue manipulation (14→89 days) → futures price impact (+18.4%, $633M) → cross-exchange arbitrage ($48M) → downstream harm ($1.4B, 340 consumers) → CFTC/LME/FCA/DOJ referral' },
    { key: 'regulatoryCompliance', label: 'Regulatory Compliance (SEC/FINRA/ESMA)', icon: <GavelIcon />, fn: actoneScenarioRegulatoryCompliance,
      desc: 'Rule threshold breach alerts (14 categories, <60s SLA) → audit trail completeness (847K events, SHA-256, 7yr retention) → alert escalation workflow (5 tiers, auto-escalation) → case management lifecycle (8 states, reopen) → 42 rules tested (12 SEC + 16 FINRA + 14 ESMA) — 100% passing' },
    { key: 'missingData', label: 'Missing Data Detection', icon: <StorageIcon />, fn: actoneScenarioMissingData,
      desc: 'Sequence gap analysis (14,283 missing trades, 62,410 orders across 4 venues) → root causes (feed drop, parser timeout, connectivity) → surveillance impact (23 alerts, 12 false negatives) → 100% recovery via venue replay → MTTD 4.2 min, MTTR 47 min' },
    { key: 'duplicateTrades', label: 'Duplicate Trade Detection', icon: <StorageIcon />, fn: actoneScenarioDuplicateTrades,
      desc: '5,056 duplicates in 4.2M trades (0.12%) → FIX retransmission (51.7%), Kafka rebalance (28.5%), venue corrections (19.8%) → 18 false-positive alerts suppressed → $142.8M notional corrected → idempotency + exactly-once controls deployed' },
    { key: 'timeSyncIssues', label: 'Time Sync Issues Detection', icon: <AccessTimeIcon />, fn: actoneScenarioTimeSyncIssues,
      desc: '6/48 systems drifted (worst 340ms) → 31,847 timestamp violations (0.76%) → 50 surveillance alerts affected (14 FP, 6 FN) → GPS PPS correction → NTP remediation all 6 systems → MiFID II RTS-25 compliant, continuous monitoring' },
    { key: 'ruleEngineTesting', label: 'Rule Engine Testing', icon: <TuneIcon />, fn: actoneScenarioRuleEngineTesting,
      desc: '70 rules (38 threshold + 24 pattern + 8 ML). Threshold: 100% boundary accuracy. Pattern: F1 0.971. ML: AUC 0.947. E2E: precision 95.7%→98.1%, recall 97.8%→98.2%, F1 0.968→0.982. FP -57.2%, FN -20.2%. 4 tuning actions, regression verified' },
  ];

  return (
    <Box>
      <Typography variant="h6" fontWeight={600} mb={2}>Investigation Scenarios</Typography>
      {scenarios.map((sc) => (
        <Accordion key={sc.key} defaultExpanded={!!results[sc.key]}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={1}>
              {sc.icon}
              <Typography fontWeight={600}>{sc.label}</Typography>
              {results[sc.key] && <Chip label={results[sc.key].final_status?.replace(/_/g, ' ')} size="small" color="success" />}
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="body2" color="text.secondary" mb={2}>{sc.desc}</Typography>
            <Button startIcon={loading[sc.key] ? <CircularProgress size={16} /> : <PlayArrowIcon />}
              onClick={() => runScenario(sc.key, sc.fn)} variant="contained" size="small" disabled={loading[sc.key]}>
              Run Scenario
            </Button>
            {results[sc.key] && (
              <Box mt={2}>
                <Grid container spacing={2} mb={2}>
                  <Grid item xs={6} md={3}><StatCard title="Case ID" value={results[sc.key].case_id} /></Grid>
                  <Grid item xs={6} md={3}><StatCard title="Priority" value={results[sc.key].priority} color={priorityColor(results[sc.key].priority) + '.main'} /></Grid>
                  <Grid item xs={6} md={3}><StatCard title="Evidence Items" value={results[sc.key].evidence_count} color="info.main" /></Grid>
                  <Grid item xs={6} md={3}><StatCard title="Duration" value={`${results[sc.key].total_duration_hours}h`} /></Grid>
                </Grid>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Steps</Typography>
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>#</TableCell><TableCell>Action</TableCell><TableCell>Result</TableCell><TableCell>Status After</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {(results[sc.key].steps || []).map((step) => (
                        <TableRow key={step.step}>
                          <TableCell>{step.step}</TableCell>
                          <TableCell><Chip label={step.action.replace(/_/g, ' ')} size="small" variant="outlined" /></TableCell>
                          <TableCell><Typography variant="body2">{step.result}</Typography></TableCell>
                          <TableCell>{step.status_after ? <Chip label={step.status_after.replace(/_/g, ' ')} size="small" color={statusColor(step.status_after)} /> : '—'}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
                {results[sc.key].sar && (
                  <Box mt={1}>
                    <Chip icon={<DescriptionIcon />} label={`SAR: ${results[sc.key].sar.sar_id} — ${results[sc.key].sar.status} (ACK: ${results[sc.key].sar.ack_number})`} color="success" />
                  </Box>
                )}
              </Box>
            )}
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
}

// ═══════════════════ Audit Trail Tab ═══════════════════

function AuditTrailTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try { const res = await getActoneAudit(); setData(res.data); }
    catch (e) { console.error('Failed to load audit:', e); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Box textAlign="center" py={4}><CircularProgress /></Box>;
  if (!data) return <Alert severity="info">Click refresh to load audit trail</Alert>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>Audit Trail</Typography>
        <Button startIcon={<RefreshIcon />} onClick={load} variant="outlined" size="small">Refresh</Button>
      </Box>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Timestamp</TableCell><TableCell>Case</TableCell>
              <TableCell>Action</TableCell><TableCell>Actor</TableCell><TableCell>Details</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(data.audit_entries || []).map((e, i) => (
              <TableRow key={i}>
                <TableCell><Typography variant="caption">{new Date(e.timestamp).toLocaleString()}</Typography></TableCell>
                <TableCell><Typography fontWeight={600} variant="body2">{e.case_id}</Typography></TableCell>
                <TableCell><Chip label={e.action.replace(/_/g, ' ')} size="small" variant="outlined" /></TableCell>
                <TableCell>{e.actor}</TableCell>
                <TableCell><Typography variant="caption">{JSON.stringify(e.details)}</Typography></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

// ═══════════════════ State Machine Tab ═══════════════════

function StateMachineTab() {
  const [data, setData] = useState(null);
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [smRes, infoRes] = await Promise.all([getActoneStateMachine(), getActoneInfo()]);
      setData(smRes.data);
      setInfo(infoRes.data);
    } catch (e) { console.error('Failed to load state machine:', e); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Box textAlign="center" py={4}><CircularProgress /></Box>;
  if (!data) return <Alert severity="info">Loading state machine...</Alert>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>State Machine & Engine Info</Typography>
        <Button startIcon={<RefreshIcon />} onClick={load} variant="outlined" size="small">Refresh</Button>
      </Box>

      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} md={3}><StatCard title="Total States" value={data.total_states} color="primary.main" /></Grid>
        <Grid item xs={6} md={3}><StatCard title="Case Types" value={data.case_types?.length} color="info.main" /></Grid>
        <Grid item xs={6} md={3}><StatCard title="Priority Levels" value={Object.keys(data.priority_sla || {}).length} color="warning.main" /></Grid>
        <Grid item xs={6} md={3}><StatCard title="Components" value={info?.total_components || 12} color="success.main" /></Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>State Transitions</Typography>
              {Object.entries(data.transitions || {}).map(([state, targets]) => (
                <Box key={state} mb={1}>
                  <Chip label={state.replace(/_/g, ' ')} size="small" color={statusColor(state)} sx={{ mr: 1 }} />
                  <Typography variant="caption" component="span">→ </Typography>
                  {targets.map((t) => (
                    <Chip key={t} label={t.replace(/_/g, ' ')} size="small" variant="outlined" sx={{ mr: 0.5, mb: 0.5 }} />
                  ))}
                </Box>
              ))}
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>Priority SLAs</Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow><TableCell>Priority</TableCell><TableCell align="center">Investigation (h)</TableCell><TableCell align="center">Resolution (h)</TableCell></TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(data.priority_sla || {}).map(([p, sla]) => (
                      <TableRow key={p}>
                        <TableCell><Chip label={p} size="small" color={priorityColor(p)} /></TableCell>
                        <TableCell align="center">{sla.investigation_hours}</TableCell>
                        <TableCell align="center">{sla.resolution_hours}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle1" fontWeight={600} gutterBottom>Engine Components</Typography>
              <List dense>
                {(info?.components || []).map((comp, i) => (
                  <ListItem key={i}>
                    <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
                    <ListItemText primary={comp.name} secondary={comp.description} />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}

// ═══════════════════ Main ActOnePage ═══════════════════

const TABS = [
  { label: 'KPI Dashboard', icon: <DashboardIcon /> },
  { label: 'Alert Triage', icon: <AssignmentIcon /> },
  { label: 'Cases', icon: <WorkIcon /> },
  { label: 'Customer 360', icon: <PersonIcon /> },
  { label: 'Scenarios', icon: <PlayArrowIcon /> },
  { label: 'Audit Trail', icon: <TimelineIcon /> },
  { label: 'State Machine & Info', icon: <AccountTreeIcon /> },
];

export default function ActOnePage() {
  const [tab, setTab] = useState(0);

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <WorkIcon sx={{ fontSize: 36, color: 'primary.main' }} />
        <Box>
          <Typography variant="h4" fontWeight={700} sx={{ fontSize: { xs: '1.5rem', md: '2.125rem' } }}>ActOne Case Management</Typography>
          <Typography variant="body2" color="text.secondary">
            Investigation Hub — Unified case management for AML, Fraud & Trading Surveillance
          </Typography>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} variant="scrollable" scrollButtons="auto"
          textColor="primary" indicatorColor="primary">
          {TABS.map((t, i) => (
            <Tab key={i} label={t.label} icon={t.icon} iconPosition="start"
              sx={{ minHeight: 48, textTransform: 'none', fontWeight: 600 }} />
          ))}
        </Tabs>
      </Paper>

      {tab === 0 && <KPIDashboardTab />}
      {tab === 1 && <AlertTriageTab />}
      {tab === 2 && <CasesTab />}
      {tab === 3 && <Customer360Tab />}
      {tab === 4 && <ScenariosTab />}
      {tab === 5 && <AuditTrailTab />}
      {tab === 6 && <StateMachineTab />}
    </Box>
  );
}
