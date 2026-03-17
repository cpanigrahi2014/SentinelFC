import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Paper, Tabs, Tab, Grid, Card, CardContent, Chip, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Alert, Dialog, DialogTitle, DialogContent, DialogActions,
  TextField, MenuItem, Select, FormControl, InputLabel, Stepper, Step, StepLabel,
  LinearProgress, Divider, IconButton, Tooltip, Accordion, AccordionSummary,
  AccordionDetails, List, ListItem, ListItemIcon, ListItemText, Badge,
} from '@mui/material';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import DashboardIcon from '@mui/icons-material/Dashboard';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import ScheduleIcon from '@mui/icons-material/Schedule';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import IntegrationInstructionsIcon from '@mui/icons-material/IntegrationInstructions';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import HourglassEmptyIcon from '@mui/icons-material/HourglassEmpty';
import RefreshIcon from '@mui/icons-material/Refresh';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import InfoIcon from '@mui/icons-material/Info';
import SyncIcon from '@mui/icons-material/Sync';
import DescriptionIcon from '@mui/icons-material/Description';
import GppBadIcon from '@mui/icons-material/GppBad';
import AssignmentTurnedInIcon from '@mui/icons-material/AssignmentTurnedIn';
import {
  getKycDashboard, getKycCases, kycOnboard, kycPeriodicReviewCheck,
  kycTriggerEvent, getKycTriggerEvents, kycIntegrate, getKycStatusMachine, getKycInfo,
} from '../services/api';

// ═══════════════════ Helper Components ═══════════════════

const riskColor = (level) => {
  const map = { critical: 'error', high: 'warning', medium: 'info', low: 'success' };
  return map[level] || 'default';
};

const statusColor = (status) => {
  const map = {
    active: 'success', renewed: 'success', refresh_due: 'warning',
    refresh_in_progress: 'info', under_review: 'info', pending_documents: 'warning',
    pending_approval: 'info', initiated: 'default', expired: 'error',
    suspended: 'error', closed: 'default',
  };
  return map[status] || 'default';
};

const severityColor = (sev) => {
  const map = { critical: 'error', high: 'warning', medium: 'info', low: 'success' };
  return map[sev] || 'default';
};

const StatCard = ({ title, value, color, subtitle }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Typography variant="body2" color="text.secondary" gutterBottom>{title}</Typography>
      <Typography variant="h4" fontWeight={700} color={color || 'text.primary'}>{value}</Typography>
      {subtitle && <Typography variant="caption" color="text.secondary">{subtitle}</Typography>}
    </CardContent>
  </Card>
);

// ═══════════════════ Dashboard Tab ═══════════════════

function DashboardTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getKycDashboard();
      setData(res.data);
    } catch (e) {
      console.error('Failed to load KYC dashboard:', e);
    }
    setLoading(false);
  }, []);

  useEffect(() => { loadDashboard(); }, [loadDashboard]);

  if (loading) return <Box textAlign="center" py={4}><CircularProgress /></Box>;
  if (!data) return <Alert severity="info">Click refresh to load KYC dashboard</Alert>;

  const sd = data.status_distribution || {};
  const rd = data.risk_distribution || {};

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>KYC Lifecycle Dashboard</Typography>
        <Button startIcon={<RefreshIcon />} onClick={loadDashboard} variant="outlined" size="small">Refresh</Button>
      </Box>

      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Total KYC Cases" value={data.total_cases} color="primary.main" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Active" value={sd.active || 0} color="success.main" subtitle="Customers in good standing" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Refresh Due / In Progress" value={(sd.refresh_due || 0) + (sd.refresh_in_progress || 0)} color="warning.main" subtitle="Require attention" />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <StatCard title="Trigger Events" value={data.total_trigger_events} color="error.main" subtitle="Total events processed" />
        </Grid>
      </Grid>

      <Grid container spacing={2} mb={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>Status Distribution</Typography>
            {Object.entries(sd).map(([status, count]) => (
              <Box key={status} display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                <Chip label={status.replace(/_/g, ' ')} color={statusColor(status)} size="small" variant="outlined" />
                <Typography fontWeight={600}>{count}</Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>Risk Distribution</Typography>
            {Object.entries(rd).map(([level, count]) => (
              <Box key={level} display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                <Chip label={level.toUpperCase()} color={riskColor(level)} size="small" />
                <Typography fontWeight={600}>{count}</Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>Recent Trigger Events</Typography>
            {(data.recent_trigger_events || []).map((evt, i) => (
              <Box key={i} display="flex" justifyContent="space-between" alignItems="center" py={0.5}
                   borderBottom={i < data.recent_trigger_events.length - 1 ? '1px solid #eee' : 'none'}>
                <Box>
                  <Chip label={evt.event_type.replace(/_/g, ' ')} color={severityColor(evt.severity)} size="small" />
                  <Typography variant="caption" ml={1}>{evt.customer_id}</Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {new Date(evt.timestamp).toLocaleString()}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>Recent Integrations</Typography>
            {(data.recent_integrations || []).map((log, i) => (
              <Box key={i} display="flex" justifyContent="space-between" alignItems="center" py={0.5}
                   borderBottom={i < data.recent_integrations.length - 1 ? '1px solid #eee' : 'none'}>
                <Box>
                  <Chip label={log.system} size="small" variant="outlined" />
                  <Typography variant="caption" ml={1}>{log.action} — {log.customer_id}</Typography>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {new Date(log.timestamp).toLocaleString()}
                </Typography>
              </Box>
            ))}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

// ═══════════════════ Onboarding Tab ═══════════════════

function OnboardingTab() {
  const [cases, setCases] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [onboardResult, setOnboardResult] = useState(null);
  const [form, setForm] = useState({
    customer_id: '', first_name: '', last_name: '', customer_type: 'individual',
    country_of_residence: 'US', pep_status: false, annual_income: 50000, age: 35,
    products: [],
  });

  const loadCases = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getKycCases();
      setCases(res.data);
    } catch (e) {
      console.error('Failed to load KYC cases:', e);
    }
    setLoading(false);
  }, []);

  useEffect(() => { loadCases(); }, [loadCases]);

  const handleOnboard = async () => {
    try {
      const res = await kycOnboard(form);
      setOnboardResult(res.data);
      loadCases();
    } catch (e) {
      console.error('Onboarding failed:', e);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>KYC Onboarding & Case Management</Typography>
        <Box>
          <Button startIcon={<PersonAddIcon />} variant="contained" size="small" onClick={() => setDialogOpen(true)} sx={{ mr: 1 }}>
            New Onboarding
          </Button>
          <Button startIcon={<RefreshIcon />} variant="outlined" size="small" onClick={loadCases}>Refresh</Button>
        </Box>
      </Box>

      {loading ? <Box textAlign="center" py={4}><CircularProgress /></Box> : cases && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 700 }}>Case ID</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Customer</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Type</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Status</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>CDD Level</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Risk</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Next Review</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(cases.cases || []).map((c) => (
                <TableRow key={c.case_id} hover>
                  <TableCell><Typography variant="body2" fontFamily="monospace">{c.case_id}</Typography></TableCell>
                  <TableCell>
                    <Typography variant="body2" fontWeight={600}>{c.customer_name}</Typography>
                    <Typography variant="caption" color="text.secondary">{c.customer_id}</Typography>
                  </TableCell>
                  <TableCell><Chip label={c.customer_type} size="small" variant="outlined" /></TableCell>
                  <TableCell><Chip label={c.status.replace(/_/g, ' ')} color={statusColor(c.status)} size="small" /></TableCell>
                  <TableCell>
                    <Chip label={c.cdd_level === 'enhanced_due_diligence' ? 'EDD' : c.cdd_level === 'simplified_due_diligence' ? 'SDD' : 'CDD'}
                          size="small" color={c.cdd_level === 'enhanced_due_diligence' ? 'error' : c.cdd_level === 'simplified_due_diligence' ? 'success' : 'info'}
                          variant="outlined" />
                  </TableCell>
                  <TableCell>
                    <Chip label={(c.risk_indicators?.risk_level || 'n/a').toUpperCase()}
                          color={riskColor(c.risk_indicators?.risk_level)} size="small" />
                  </TableCell>
                  <TableCell>
                    {c.next_review_date ? new Date(c.next_review_date).toLocaleDateString() : '—'}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Onboarding Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>New Customer Onboarding</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12} sm={6}>
              <TextField label="Customer ID" fullWidth size="small" value={form.customer_id}
                onChange={(e) => setForm({ ...form, customer_id: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>Customer Type</InputLabel>
                <Select value={form.customer_type} label="Customer Type"
                  onChange={(e) => setForm({ ...form, customer_type: e.target.value })}>
                  <MenuItem value="individual">Individual</MenuItem>
                  <MenuItem value="corporate">Corporate</MenuItem>
                  <MenuItem value="business">Business</MenuItem>
                  <MenuItem value="trust">Trust</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="First Name" fullWidth size="small" value={form.first_name}
                onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Last Name" fullWidth size="small" value={form.last_name}
                onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Country (ISO)" fullWidth size="small" value={form.country_of_residence}
                onChange={(e) => setForm({ ...form, country_of_residence: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth size="small">
                <InputLabel>PEP Status</InputLabel>
                <Select value={form.pep_status} label="PEP Status"
                  onChange={(e) => setForm({ ...form, pep_status: e.target.value })}>
                  <MenuItem value={false}>No</MenuItem>
                  <MenuItem value={true}>Yes</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Annual Income" fullWidth size="small" type="number" value={form.annual_income}
                onChange={(e) => setForm({ ...form, annual_income: Number(e.target.value) })} />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField label="Age" fullWidth size="small" type="number" value={form.age}
                onChange={(e) => setForm({ ...form, age: Number(e.target.value) })} />
            </Grid>
          </Grid>

          {onboardResult && (
            <Box mt={2}>
              <Alert severity={onboardResult.cdd_level === 'enhanced_due_diligence' ? 'warning' : 'success'} sx={{ mb: 1 }}>
                <strong>{onboardResult.case_id}</strong> — CDD Level: {onboardResult.cdd_level === 'enhanced_due_diligence' ? 'Enhanced Due Diligence (EDD)' :
                  onboardResult.cdd_level === 'simplified_due_diligence' ? 'Simplified DD' : 'Standard CDD'}
                &nbsp;| Risk: {onboardResult.risk_indicators?.risk_level?.toUpperCase()}
                &nbsp;| Score: {onboardResult.risk_indicators?.initial_score}
              </Alert>
              <Typography variant="subtitle2" fontWeight={600}>Required Documents ({onboardResult.required_documents?.length})</Typography>
              {(onboardResult.required_documents || []).map((d, i) => (
                <Chip key={i} label={d.label} size="small" sx={{ mr: 0.5, mb: 0.5 }} icon={<DescriptionIcon />} />
              ))}
              <Typography variant="subtitle2" fontWeight={600} mt={1}>Onboarding Checklist ({onboardResult.checklist?.length} tasks)</Typography>
              {(onboardResult.checklist || []).map((t, i) => (
                <Box key={i} display="flex" alignItems="center" gap={0.5}>
                  <HourglassEmptyIcon fontSize="small" color="action" />
                  <Typography variant="body2">{t.label}</Typography>
                  {t.required && <Chip label="Required" size="small" color="error" variant="outlined" sx={{ ml: 'auto' }} />}
                </Box>
              ))}
              {(onboardResult.risk_indicators?.flags || []).length > 0 && (
                <>
                  <Typography variant="subtitle2" fontWeight={600} mt={1}>Risk Flags</Typography>
                  {onboardResult.risk_indicators.flags.map((f, i) => (
                    <Chip key={i} label={f.replace(/_/g, ' ')} color="warning" size="small" sx={{ mr: 0.5, mb: 0.5 }} />
                  ))}
                </>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setDialogOpen(false); setOnboardResult(null); }}>Close</Button>
          <Button variant="contained" onClick={handleOnboard} startIcon={<PlayArrowIcon />}>Run Onboarding</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

// ═══════════════════ Periodic Reviews Tab ═══════════════════

function PeriodicReviewsTab() {
  const [reviewData, setReviewData] = useState(null);
  const [loading, setLoading] = useState(false);

  const runCheck = async () => {
    setLoading(true);
    try {
      const res = await kycPeriodicReviewCheck();
      setReviewData(res.data);
    } catch (e) {
      console.error('Periodic review check failed:', e);
    }
    setLoading(false);
  };

  useEffect(() => { runCheck(); }, []);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>Periodic Review Automation</Typography>
        <Button startIcon={<ScheduleIcon />} variant="contained" size="small" onClick={runCheck}>
          Run Review Check
        </Button>
      </Box>

      <Alert severity="info" sx={{ mb: 2 }}>
        Reviews are scheduled based on customer risk level: <strong>Critical</strong> = monthly (30d),
        <strong> High</strong> = quarterly (90d), <strong> Medium</strong> = annually (365d),
        <strong> Low</strong> = every 3 years (1095d). Overdue cases are auto-transitioned to <em>refresh_due</em>.
      </Alert>

      {loading ? <Box textAlign="center" py={4}><CircularProgress /></Box> : reviewData && (
        <>
          <Grid container spacing={2} mb={3}>
            <Grid item xs={6} sm={3}>
              <StatCard title="Active Cases" value={reviewData.active_cases} color="primary.main" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatCard title="Overdue" value={reviewData.overdue_count} color="error.main" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatCard title="Due in 30 Days" value={reviewData.due_within_30d_count} color="warning.main" />
            </Grid>
            <Grid item xs={6} sm={3}>
              <StatCard title="Due in 90 Days" value={reviewData.due_within_90d_count} color="info.main" />
            </Grid>
          </Grid>

          {reviewData.overdue_count > 0 && (
            <Paper sx={{ p: 2, mb: 2, borderLeft: '4px solid #d32f2f' }}>
              <Typography variant="subtitle1" fontWeight={600} color="error.main" gutterBottom>
                ⚠ Overdue Reviews ({reviewData.overdue_count})
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ fontWeight: 700 }}>Customer</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Case ID</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Risk</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>CDD Level</TableCell>
                      <TableCell sx={{ fontWeight: 700 }}>Days Overdue</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {(reviewData.overdue || []).map((r, i) => (
                      <TableRow key={i}>
                        <TableCell>
                          <Typography variant="body2" fontWeight={600}>{r.customer_name}</Typography>
                          <Typography variant="caption" color="text.secondary">{r.customer_id}</Typography>
                        </TableCell>
                        <TableCell><Typography fontFamily="monospace" variant="body2">{r.case_id}</Typography></TableCell>
                        <TableCell><Chip label={r.risk_level.toUpperCase()} color={riskColor(r.risk_level)} size="small" /></TableCell>
                        <TableCell><Chip label={r.cdd_level === 'enhanced_due_diligence' ? 'EDD' : 'CDD'} size="small" variant="outlined" /></TableCell>
                        <TableCell><Chip label={`${r.days_overdue}d`} color="error" size="small" /></TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          )}

          {reviewData.due_within_30d_count > 0 && (
            <Paper sx={{ p: 2, mb: 2, borderLeft: '4px solid #f57c00' }}>
              <Typography variant="subtitle1" fontWeight={600} color="warning.main" gutterBottom>
                Due Within 30 Days ({reviewData.due_within_30d_count})
              </Typography>
              {(reviewData.due_within_30d || []).map((r, i) => (
                <Box key={i} display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
                  <Box>
                    <Typography variant="body2" fontWeight={600}>{r.customer_name}</Typography>
                    <Typography variant="caption" color="text.secondary">{r.customer_id} — {r.case_id}</Typography>
                  </Box>
                  <Chip label={`${r.days_until_review}d remaining`} color="warning" size="small" variant="outlined" />
                </Box>
              ))}
            </Paper>
          )}

          {reviewData.due_within_90d_count > 0 && (
            <Paper sx={{ p: 2, borderLeft: '4px solid #1976d2' }}>
              <Typography variant="subtitle1" fontWeight={600} color="info.main" gutterBottom>
                Due Within 90 Days ({reviewData.due_within_90d_count})
              </Typography>
              {(reviewData.due_within_90d || []).map((r, i) => (
                <Box key={i} display="flex" justifyContent="space-between" alignItems="center" py={0.5}>
                  <Box>
                    <Typography variant="body2" fontWeight={600}>{r.customer_name}</Typography>
                    <Typography variant="caption" color="text.secondary">{r.customer_id} — {r.case_id}</Typography>
                  </Box>
                  <Chip label={`${r.days_until_review}d remaining`} color="info" size="small" variant="outlined" />
                </Box>
              ))}
            </Paper>
          )}
        </>
      )}
    </Box>
  );
}

// ═══════════════════ Trigger Events Tab ═══════════════════

function TriggerEventsTab() {
  const [events, setEvents] = useState(null);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [triggerResult, setTriggerResult] = useState(null);
  const [form, setForm] = useState({
    customer_id: 'CUST-003', event_type: 'sanctions_hit',
  });

  const EVENT_TYPES = [
    { value: 'sanctions_hit', label: 'Sanctions Hit', severity: 'critical' },
    { value: 'adverse_media', label: 'Adverse Media', severity: 'high' },
    { value: 'pep_status_change', label: 'PEP Status Change', severity: 'high' },
    { value: 'unusual_activity', label: 'Unusual Activity', severity: 'medium' },
    { value: 'account_dormancy_reactivation', label: 'Dormancy Reactivation', severity: 'medium' },
    { value: 'large_transaction', label: 'Large Transaction', severity: 'medium' },
    { value: 'country_risk_change', label: 'Country Risk Change', severity: 'high' },
    { value: 'customer_info_change', label: 'Customer Info Change', severity: 'low' },
    { value: 'regulatory_request', label: 'Regulatory Request', severity: 'critical' },
    { value: 'law_enforcement_request', label: 'Law Enforcement Request', severity: 'critical' },
  ];

  const loadEvents = useCallback(async () => {
    setLoading(true);
    try {
      const res = await getKycTriggerEvents();
      setEvents(res.data);
    } catch (e) {
      console.error('Failed to load trigger events:', e);
    }
    setLoading(false);
  }, []);

  useEffect(() => { loadEvents(); }, [loadEvents]);

  const handleTrigger = async () => {
    try {
      const res = await kycTriggerEvent(form);
      setTriggerResult(res.data);
      loadEvents();
    } catch (e) {
      console.error('Trigger event failed:', e);
    }
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6" fontWeight={600}>Trigger-Based Review Events</Typography>
        <Box>
          <Button startIcon={<WarningAmberIcon />} variant="contained" size="small" color="warning"
            onClick={() => setDialogOpen(true)} sx={{ mr: 1 }}>
            Simulate Trigger
          </Button>
          <Button startIcon={<RefreshIcon />} variant="outlined" size="small" onClick={loadEvents}>Refresh</Button>
        </Box>
      </Box>

      <Alert severity="warning" sx={{ mb: 2 }}>
        Trigger events automatically initiate KYC reviews based on severity:
        <strong> Critical</strong> (sanctions hit, regulatory request) → Immediate review |
        <strong> High</strong> (adverse media, PEP change) → Priority scheduling |
        <strong> Medium</strong> (unusual activity) → Flagged for next review.
      </Alert>

      {loading ? <Box textAlign="center" py={4}><CircularProgress /></Box> : events && (
        <TableContainer component={Paper}>
          <Table size="small">
            <TableHead>
              <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                <TableCell sx={{ fontWeight: 700 }}>Event ID</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Customer</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Event Type</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Severity</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Action Taken</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Review Required</TableCell>
                <TableCell sx={{ fontWeight: 700 }}>Timestamp</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {(events.events || []).map((evt) => (
                <TableRow key={evt.event_id} hover>
                  <TableCell><Typography fontFamily="monospace" variant="body2">{evt.event_id}</Typography></TableCell>
                  <TableCell>{evt.customer_id}</TableCell>
                  <TableCell><Chip label={evt.event_type.replace(/_/g, ' ')} size="small" /></TableCell>
                  <TableCell><Chip label={evt.severity.toUpperCase()} color={severityColor(evt.severity)} size="small" /></TableCell>
                  <TableCell><Typography variant="body2">{evt.auto_action_taken?.replace(/_/g, ' ')}</Typography></TableCell>
                  <TableCell>
                    {evt.review_required ? <CheckCircleIcon color="error" fontSize="small" /> : <Typography variant="body2">—</Typography>}
                  </TableCell>
                  <TableCell><Typography variant="caption">{new Date(evt.timestamp).toLocaleString()}</Typography></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {/* Trigger Simulation Dialog */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Simulate Trigger Event</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 0.5 }}>
            <Grid item xs={12}>
              <TextField label="Customer ID" fullWidth size="small" value={form.customer_id}
                onChange={(e) => setForm({ ...form, customer_id: e.target.value })} />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth size="small">
                <InputLabel>Event Type</InputLabel>
                <Select value={form.event_type} label="Event Type"
                  onChange={(e) => setForm({ ...form, event_type: e.target.value })}>
                  {EVENT_TYPES.map((et) => (
                    <MenuItem key={et.value} value={et.value}>
                      {et.label} ({et.severity})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
          </Grid>

          {triggerResult && (
            <Alert severity={triggerResult.severity === 'critical' ? 'error' : triggerResult.severity === 'high' ? 'warning' : 'info'} sx={{ mt: 2 }}>
              <strong>{triggerResult.event_id}</strong> — {triggerResult.event_type.replace(/_/g, ' ')}
              <br />Severity: {triggerResult.severity.toUpperCase()} | Action: {triggerResult.auto_action_taken?.replace(/_/g, ' ')}
              {triggerResult.review_required && <><br /><strong>⚠ Immediate review triggered</strong></>}
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => { setDialogOpen(false); setTriggerResult(null); }}>Close</Button>
          <Button variant="contained" color="warning" onClick={handleTrigger} startIcon={<WarningAmberIcon />}>
            Fire Trigger
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}

// ═══════════════════ Integrations Tab ═══════════════════

function IntegrationsTab() {
  const [results, setResults] = useState({});
  const [loading, setLoading] = useState({});
  const [customerId, setCustomerId] = useState('CUST-001');

  const syncSystem = async (system) => {
    setLoading((prev) => ({ ...prev, [system]: true }));
    try {
      const res = await kycIntegrate(system, customerId);
      setResults((prev) => ({ ...prev, [system]: res.data }));
    } catch (e) {
      console.error(`Integration sync failed for ${system}:`, e);
    }
    setLoading((prev) => ({ ...prev, [system]: false }));
  };

  const systems = [
    { key: 'crm', label: 'CRM / Relationship Management', icon: <PersonAddIcon />,
      description: 'Sync relationship data: RM assignment, customer segment, products held, relationship value, contact history' },
    { key: 'core-banking', label: 'Core Banking System', icon: <IntegrationInstructionsIcon />,
      description: 'Sync account data: balances, transaction volumes, dormancy flags, freeze status, account types' },
    { key: 'digital-onboarding', label: 'Digital Onboarding Platform', icon: <VerifiedUserIcon />,
      description: 'Sync verification data: liveness check, OCR/NFC ID verification, biometric enrollment, device fingerprint' },
  ];

  return (
    <Box>
      <Typography variant="h6" fontWeight={600} mb={2}>Integration Layer</Typography>

      <Alert severity="info" sx={{ mb: 2 }}>
        Sync KYC data with external systems. Each integration call is logged in the audit trail.
      </Alert>

      <Box display="flex" alignItems="center" gap={2} mb={3}>
        <TextField label="Customer ID" value={customerId} size="small"
          onChange={(e) => setCustomerId(e.target.value)} sx={{ width: { xs: '100%', sm: 200 } }} />
        <Typography variant="body2" color="text.secondary">Select a customer ID to sync with integrations</Typography>
      </Box>

      {systems.map((sys) => (
        <Accordion key={sys.key} sx={{ mb: 1 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={1.5} width="100%">
              {sys.icon}
              <Box flex={1}>
                <Typography fontWeight={600}>{sys.label}</Typography>
                <Typography variant="caption" color="text.secondary">{sys.description}</Typography>
              </Box>
              <Button variant="outlined" size="small" startIcon={loading[sys.key] ? <CircularProgress size={16} /> : <SyncIcon />}
                onClick={(e) => { e.stopPropagation(); syncSystem(sys.key); }}
                disabled={loading[sys.key]}>
                Sync
              </Button>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            {results[sys.key] ? (
              <Paper sx={{ p: 2, backgroundColor: '#f9f9f9' }}>
                <pre style={{ fontSize: 12, margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
                  {JSON.stringify(results[sys.key], null, 2)}
                </pre>
              </Paper>
            ) : (
              <Typography variant="body2" color="text.secondary">Click "Sync" to fetch integration data</Typography>
            )}
          </AccordionDetails>
        </Accordion>
      ))}
    </Box>
  );
}

// ═══════════════════ Status Machine Tab ═══════════════════

function StatusMachineTab() {
  const [machineData, setMachineData] = useState(null);
  const [infoData, setInfoData] = useState(null);
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [machineRes, infoRes] = await Promise.all([getKycStatusMachine(), getKycInfo()]);
      setMachineData(machineRes.data);
      setInfoData(infoRes.data);
    } catch (e) {
      console.error('Failed to load status machine:', e);
    }
    setLoading(false);
  }, []);

  useEffect(() => { loadData(); }, [loadData]);

  if (loading) return <Box textAlign="center" py={4}><CircularProgress /></Box>;

  return (
    <Box>
      <Typography variant="h6" fontWeight={600} mb={2}>KYC Status State Machine & Engine Info</Typography>

      {infoData && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            {infoData.engine} v{infoData.version}
          </Typography>
          <Grid container spacing={2} mb={2}>
            <Grid item xs={6} sm={3}><StatCard title="Components" value={infoData.total_components} /></Grid>
            <Grid item xs={6} sm={3}><StatCard title="Status States" value={infoData.status_states} /></Grid>
            <Grid item xs={6} sm={3}><StatCard title="Trigger Types" value={infoData.trigger_event_types} /></Grid>
            <Grid item xs={6} sm={3}><StatCard title="CDD Levels" value={infoData.cdd_levels?.length} /></Grid>
          </Grid>

          <Typography variant="subtitle2" fontWeight={600} gutterBottom>Components</Typography>
          <Grid container spacing={1} mb={2}>
            {(infoData.components || []).map((comp, i) => (
              <Grid item xs={12} md={6} key={i}>
                <Card variant="outlined" sx={{ p: 1.5 }}>
                  <Box display="flex" alignItems="center" gap={1}>
                    <CheckCircleIcon color="success" fontSize="small" />
                    <Typography variant="body2" fontWeight={600}>{comp.name}</Typography>
                    <Chip label={comp.status} color="success" size="small" sx={{ ml: 'auto' }} />
                  </Box>
                  <Typography variant="caption" color="text.secondary">{comp.description}</Typography>
                </Card>
              </Grid>
            ))}
          </Grid>

          <Typography variant="subtitle2" fontWeight={600} gutterBottom>Review Frequencies</Typography>
          <Box display="flex" gap={1} flexWrap="wrap" mb={2}>
            {infoData.review_frequencies && Object.entries(infoData.review_frequencies).map(([level, freq]) => (
              <Chip key={level} label={`${level.toUpperCase()}: ${freq}`} color={riskColor(level)} variant="outlined" size="small" />
            ))}
          </Box>

          <Typography variant="subtitle2" fontWeight={600} gutterBottom>Key Scenarios</Typography>
          {(infoData.scenarios || []).map((s, i) => (
            <Alert key={i} severity="info" sx={{ mb: 0.5 }} icon={<AssignmentTurnedInIcon />}>
              {s}
            </Alert>
          ))}
        </Paper>
      )}

      {machineData && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" fontWeight={600} gutterBottom>State Machine Transitions</Typography>
          <Typography variant="body2" color="text.secondary" mb={2}>
            11 states with enforced valid transitions. Invalid transitions are rejected.
          </Typography>

          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
                  <TableCell sx={{ fontWeight: 700, width: 200 }}>Current State</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Valid Next States</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {machineData.transitions && Object.entries(machineData.transitions).map(([state, nexts]) => (
                  <TableRow key={state}>
                    <TableCell><Chip label={state.replace(/_/g, ' ')} color={statusColor(state)} size="small" /></TableCell>
                    <TableCell>
                      {nexts.length > 0 ? nexts.map((n, i) => (
                        <Chip key={i} label={n.replace(/_/g, ' ')} size="small" variant="outlined"
                          color={statusColor(n)} sx={{ mr: 0.5, mb: 0.3 }} />
                      )) : <Typography variant="caption" color="text.secondary">Terminal state (no transitions)</Typography>}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2" fontWeight={600} gutterBottom>Trigger Event Types</Typography>
          <Box display="flex" gap={0.5} flexWrap="wrap">
            {(machineData.trigger_event_types || []).map((t, i) => (
              <Chip key={i} label={t.replace(/_/g, ' ')} size="small" variant="outlined" />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ Main KYCPage Component ═══════════════════

export default function KYCPage() {
  const [subTab, setSubTab] = useState(0);

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1.5} mb={2}>
        <VerifiedUserIcon sx={{ fontSize: 32, color: 'primary.main' }} />
        <Box>
          <Typography variant="h5" fontWeight={700}>KYC / CDD Lifecycle Management</Typography>
          <Typography variant="body2" color="text.secondary">
            Onboarding, document verification, risk scoring, periodic reviews, trigger events &amp; integrations
          </Typography>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={subTab} onChange={(_, v) => setSubTab(v)} variant="scrollable" scrollButtons="auto"
          sx={{ '& .MuiTab-root': { fontWeight: 600 } }}>
          <Tab icon={<DashboardIcon />} iconPosition="start" label="Dashboard" />
          <Tab icon={<PersonAddIcon />} iconPosition="start" label="Onboarding & Cases" />
          <Tab icon={<ScheduleIcon />} iconPosition="start" label="Periodic Reviews" />
          <Tab icon={<WarningAmberIcon />} iconPosition="start" label="Trigger Events" />
          <Tab icon={<IntegrationInstructionsIcon />} iconPosition="start" label="Integrations" />
          <Tab icon={<AccountTreeIcon />} iconPosition="start" label="Status Machine & Info" />
        </Tabs>
      </Paper>

      {subTab === 0 && <DashboardTab />}
      {subTab === 1 && <OnboardingTab />}
      {subTab === 2 && <PeriodicReviewsTab />}
      {subTab === 3 && <TriggerEventsTab />}
      {subTab === 4 && <IntegrationsTab />}
      {subTab === 5 && <StatusMachineTab />}
    </Box>
  );
}
