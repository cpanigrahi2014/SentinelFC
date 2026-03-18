import React, { useState, useEffect } from 'react';
import {
  Box, Typography, Card, CardContent, Grid, Chip, Table, TableBody,
  TableCell, TableContainer, TableHead, TableRow, Paper, IconButton,
  Button, Dialog, DialogTitle, DialogContent, DialogActions, TextField,
  MenuItem, Alert, CircularProgress, Tooltip, LinearProgress, Divider,
  Tabs, Tab, Collapse, Accordion, AccordionSummary, AccordionDetails,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningIcon from '@mui/icons-material/Warning';
import RefreshIcon from '@mui/icons-material/Refresh';
import StorageIcon from '@mui/icons-material/Storage';
import SyncIcon from '@mui/icons-material/Sync';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import LockIcon from '@mui/icons-material/Lock';
import ScheduleIcon from '@mui/icons-material/Schedule';
import SpeedIcon from '@mui/icons-material/Speed';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import PlaylistAddCheckIcon from '@mui/icons-material/PlaylistAddCheck';
import AccountTreeIcon from '@mui/icons-material/AccountTree';
import AssessmentIcon from '@mui/icons-material/Assessment';
import GppGoodIcon from '@mui/icons-material/GppGood';
import RocketLaunchIcon from '@mui/icons-material/RocketLaunch';
import ArrowForwardIcon from '@mui/icons-material/ArrowForward';
import MonitorHeartIcon from '@mui/icons-material/MonitorHeart';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import DescriptionIcon from '@mui/icons-material/Description';
import HistoryIcon from '@mui/icons-material/History';
import PersonIcon from '@mui/icons-material/Person';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import SecurityIcon from '@mui/icons-material/Security';
import CancelIcon from '@mui/icons-material/Cancel';
import TimerIcon from '@mui/icons-material/Timer';
import PersonSearchIcon from '@mui/icons-material/PersonSearch';
import FilterListIcon from '@mui/icons-material/FilterList';
import GavelIcon from '@mui/icons-material/Gavel';
import ShieldIcon from '@mui/icons-material/Shield';
import DevicesIcon from '@mui/icons-material/Devices';
import FingerprintIcon from '@mui/icons-material/Fingerprint';
import CreditCardIcon from '@mui/icons-material/CreditCard';
import PaymentIcon from '@mui/icons-material/Payment';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import VpnKeyIcon from '@mui/icons-material/VpnKey';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import {
  getDataSources, testDataSourceConnection, verifyAllConnections, getFieldMappings,
  runTestIngestion, verifyExternalFeeds, runTestPipeline, getDataSourceMetrics,
  getDataSourceInventory, verifyCapabilities, getCustomerProfiles, checkOverdueReviews,
  getEddWorkflows, screenPEP, screenAdverseMedia,
  wlfScreenPayment, wlfScreenBatch, wlfScreenName, getWlfAlerts, getWlfAlertGroups, getWlfAlertStats,
  efmAtoSimulate, efmMuleSimulate, efmCardSimulate, efmDeviceSimulate,
  efmBiometricsSimulate, efmPaymentSimulate, efmCrossChannelSimulate, getEfmInfo,
  dbfLoginAnomalySimulate, dbfSessionHijackSimulate, dbfBotSimulate,
  dbfSocialEngineeringSimulate, getDbfInfo,
  pmfAchSimulate, pmfWireSimulate, pmfRtpZelleSimulate,
  pmfCnpSimulate, pmfCheckSimulate, getPmfInfo,
} from '../services/api';

const STATUS_CONFIG = {
  connected: { color: 'success', icon: <CheckCircleIcon fontSize="small" />, label: 'Connected' },
  degraded: { color: 'warning', icon: <WarningIcon fontSize="small" />, label: 'Degraded' },
  disconnected: { color: 'error', icon: <ErrorIcon fontSize="small" />, label: 'Disconnected' },
};

const CATEGORY_COLORS = {
  'Core Banking': '#1a237e',
  'Card / POS / ATM': '#4a148c',
  'Wire / ACH': '#006064',
  'Mobile / Online Banking': '#1b5e20',
  'KYC / Customer Data': '#e65100',
  'Device / IP / Geo': '#b71c1c',
  'External Feeds': '#263238',
};

const MAPPING_STATUS_CONFIG = {
  mapped: { color: 'success', label: 'Mapped', icon: <CheckCircleIcon fontSize="small" /> },
  not_applicable: { color: 'default', label: 'N/A', icon: <InfoOutlinedIcon fontSize="small" /> },
  enrichment_only: { color: 'info', label: 'Enrichment', icon: <InfoOutlinedIcon fontSize="small" /> },
  unmapped: { color: 'error', label: 'Unmapped', icon: <ErrorIcon fontSize="small" /> },
};

function FieldMappingTab({ fieldMappings, fieldMappingsLoading, setFieldMappings, setFieldMappingsLoading }) {
  const [expandedSource, setExpandedSource] = useState(null);

  useEffect(() => {
    if (!fieldMappings && !fieldMappingsLoading) {
      setFieldMappingsLoading(true);
      getFieldMappings()
        .then((res) => setFieldMappings(res.data))
        .catch(() => setFieldMappings(null))
        .finally(() => setFieldMappingsLoading(false));
    }
  }, [fieldMappings, fieldMappingsLoading, setFieldMappings, setFieldMappingsLoading]);

  if (fieldMappingsLoading || !fieldMappings) {
    return (
      <Box display="flex" justifyContent="center" py={6}>
        <CircularProgress />
      </Box>
    );
  }

  const { aml_schema, summaries, all_required_mapped, field_mappings } = fieldMappings;
  const requiredFields = aml_schema.filter((f) => f.required);
  const optionalFields = aml_schema.filter((f) => !f.required);
  const fullyMapped = summaries.filter((s) => s.all_required_mapped).length;

  return (
    <>
      {/* Summary banner */}
      <Alert
        severity={all_required_mapped ? 'success' : 'warning'}
        icon={all_required_mapped ? <CheckCircleIcon /> : <WarningIcon />}
        sx={{ mb: 2 }}
      >
        {all_required_mapped
          ? `All ${summaries.length} data sources have required AML fields mapped.`
          : `${fullyMapped} of ${summaries.length} sources have all required AML fields mapped.`}
      </Alert>

      {/* AML Schema reference */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="subtitle1" fontWeight={700} mb={1}>
          AML Schema &mdash; Required Fields ({requiredFields.length})
        </Typography>
        <Box display="flex" flexWrap="wrap" gap={1} mb={1}>
          {requiredFields.map((f) => (
            <Tooltip key={f.aml_field} title={`${f.data_type} — ${f.description}`}>
              <Chip label={f.aml_field} size="small" color="primary" variant="outlined" />
            </Tooltip>
          ))}
        </Box>
        <Typography variant="subtitle2" fontWeight={600} mt={2} mb={1}>
          Optional / Enrichment Fields ({optionalFields.length})
        </Typography>
        <Box display="flex" flexWrap="wrap" gap={1}>
          {optionalFields.map((f) => (
            <Tooltip key={f.aml_field} title={`${f.data_type} — ${f.description}`}>
              <Chip label={f.aml_field} size="small" variant="outlined" />
            </Tooltip>
          ))}
        </Box>
      </Paper>

      {/* Per-source accordion */}
      {summaries.map((summary) => {
        const fm = field_mappings[summary.source_id];
        const coveragePct = summary.total_required > 0
          ? Math.round((summary.mapped_required / summary.total_required) * 100)
          : 0;

        return (
          <Accordion
            key={summary.source_id}
            expanded={expandedSource === summary.source_id}
            onChange={() => setExpandedSource(expandedSource === summary.source_id ? null : summary.source_id)}
            sx={{ mb: 1 }}
          >
            <AccordionSummary expandIcon={<ExpandMoreIcon />}>
              <Box display="flex" alignItems="center" justifyContent="space-between" width="100%" pr={1}>
                <Box display="flex" alignItems="center" gap={1.5}>
                  {summary.all_required_mapped
                    ? <CheckCircleIcon color="success" />
                    : <WarningIcon color="warning" />}
                  <Box>
                    <Typography fontWeight={600}>{summary.source_name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      {summary.source_id} &bull; {summary.category}
                    </Typography>
                  </Box>
                </Box>
                <Box display="flex" alignItems="center" gap={2}>
                  <Box sx={{ minWidth: { xs: 80, sm: 140 } }}>
                    <Box display="flex" justifyContent="space-between" mb={0.25}>
                      <Typography variant="caption">Required</Typography>
                      <Typography variant="caption" fontWeight={600}>
                        {summary.mapped_required}/{summary.total_required}
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={coveragePct}
                      color={coveragePct === 100 ? 'success' : 'warning'}
                      sx={{ height: 6, borderRadius: 3 }}
                    />
                  </Box>
                  <Chip
                    label={`${summary.total_mappings} fields`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {fm ? (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow sx={{ bgcolor: 'grey.50' }}>
                        <TableCell sx={{ fontWeight: 700 }}>AML Field</TableCell>
                        <TableCell sx={{ fontWeight: 700 }}>Source Field</TableCell>
                        <TableCell sx={{ fontWeight: 700 }}>Transform</TableCell>
                        <TableCell sx={{ fontWeight: 700 }} align="center">Status</TableCell>
                        <TableCell sx={{ fontWeight: 700 }}>Notes</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {fm.mappings.map((m, idx) => {
                        const sc = MAPPING_STATUS_CONFIG[m.status] || MAPPING_STATUS_CONFIG.unmapped;
                        const isRequired = requiredFields.some((f) => f.aml_field === m.aml_field);
                        return (
                          <TableRow key={idx} sx={{ '&:last-child td': { borderBottom: 0 } }}>
                            <TableCell>
                              <Box display="flex" alignItems="center" gap={0.5}>
                                <Typography variant="body2" fontFamily="monospace" fontWeight={600}>
                                  {m.aml_field}
                                </Typography>
                                {isRequired && (
                                  <Chip label="REQ" size="small" color="primary" sx={{ height: 18, fontSize: 10 }} />
                                )}
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" fontFamily="monospace">
                                {m.source_field || '—'}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" fontFamily="monospace" color="text.secondary" fontSize={12}>
                                {m.transform || '—'}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Chip
                                icon={sc.icon}
                                label={sc.label}
                                size="small"
                                color={sc.color}
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" color="text.secondary" fontSize={12}>
                                {m.notes || '—'}
                              </Typography>
                            </TableCell>
                          </TableRow>
                        );
                      })}
                    </TableBody>
                  </Table>
                </TableContainer>
              ) : (
                <Alert severity="warning">No field mapping data available for this source.</Alert>
              )}
              {summary.unmapped_required.length > 0 && (
                <Alert severity="warning" sx={{ mt: 1 }}>
                  <strong>Unmapped required fields: </strong>
                  {summary.unmapped_required.join(', ')}
                </Alert>
              )}
            </AccordionDetails>
          </Accordion>
        );
      })}
    </>
  );
}

const FREQ_CHIP = {
  'real-time': { color: 'success', label: 'Real-time' },
  'near-real-time': { color: 'info', label: 'Near Real-time' },
  batch: { color: 'warning', label: 'Batch' },
};

function DataQualityTab({ ingestionResults, ingestionRunning, setIngestionResults, setIngestionRunning }) {
  const [expandedSource, setExpandedSource] = useState(null);

  const handleRunIngestion = async () => {
    setIngestionRunning(true);
    try {
      const res = await runTestIngestion();
      setIngestionResults(res.data);
    } catch {
      setIngestionResults(null);
    } finally {
      setIngestionRunning(false);
    }
  };

  const r = ingestionResults;

  return (
    <>
      {/* Action Bar */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <Box>
          <Typography variant="subtitle1" fontWeight={700}>
            Test Ingestion &amp; Data Quality Validation
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Sends {r ? r.sample_per_source : 50} sample transactions per source, validates field completeness, and checks timeliness SLAs.
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={ingestionRunning ? <CircularProgress size={18} color="inherit" /> : <PlaylistAddCheckIcon />}
          onClick={handleRunIngestion}
          disabled={ingestionRunning}
        >
          {ingestionRunning ? 'Running...' : 'Run Test Ingestion'}
        </Button>
      </Paper>

      {!r && !ingestionRunning && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Click <strong>Run Test Ingestion</strong> to send sample transactions from all 16 sources and validate data quality.
        </Alert>
      )}

      {ingestionRunning && (
        <Box display="flex" justifyContent="center" py={6}>
          <CircularProgress />
        </Box>
      )}

      {r && !ingestionRunning && (
        <>
          {/* Overall Summary Cards */}
          <Grid container spacing={2} mb={3}>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Total Records</Typography>
                  <Typography variant="h5" fontWeight={700}>{r.total_records.toLocaleString()}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Valid Records</Typography>
                  <Typography variant="h5" fontWeight={700} color="success.main">{r.total_valid.toLocaleString()}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Completeness</Typography>
                  <Typography variant="h5" fontWeight={700} color={r.overall_completeness_pct >= 99 ? 'success.main' : 'warning.main'}>
                    {r.overall_completeness_pct}%
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Sources Passed</Typography>
                  <Typography variant="h5" fontWeight={700} color={r.all_quality_pass ? 'success.main' : 'warning.main'}>
                    {r.passed}/{r.total_sources}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Overall banner */}
          <Alert
            severity={r.all_quality_pass ? 'success' : 'warning'}
            icon={r.all_quality_pass ? <CheckCircleIcon /> : <WarningIcon />}
            sx={{ mb: 2 }}
          >
            {r.all_quality_pass
              ? `All ${r.total_sources} sources passed data quality validation. High data quality — no gaps, no delays.`
              : `${r.passed} of ${r.total_sources} sources passed. ${r.failed} source(s) have quality issues.`}
          </Alert>

          {/* Per-source results */}
          {r.source_results.map((sr) => {
            const fc = FREQ_CHIP[sr.update_frequency] || FREQ_CHIP.batch;
            return (
              <Accordion
                key={sr.source_id}
                expanded={expandedSource === sr.source_id}
                onChange={() => setExpandedSource(expandedSource === sr.source_id ? null : sr.source_id)}
                sx={{ mb: 1 }}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" justifyContent="space-between" width="100%" pr={1}>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      {sr.quality_pass
                        ? <CheckCircleIcon color="success" />
                        : <ErrorIcon color="error" />}
                      <Box>
                        <Typography fontWeight={600}>{sr.source_name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {sr.source_id} &bull; {sr.category}
                        </Typography>
                      </Box>
                    </Box>
                    <Box display="flex" alignItems="center" gap={2}>
                      <Chip label={fc.label} size="small" color={fc.color} variant="outlined" />
                      <Box sx={{ minWidth: { xs: 80, sm: 120 } }}>
                        <Box display="flex" justifyContent="space-between" mb={0.25}>
                          <Typography variant="caption">Completeness</Typography>
                          <Typography variant="caption" fontWeight={600}>{sr.completeness_pct}%</Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={sr.completeness_pct}
                          color={sr.completeness_pct >= 99 ? 'success' : sr.completeness_pct >= 95 ? 'warning' : 'error'}
                          sx={{ height: 6, borderRadius: 3 }}
                        />
                      </Box>
                      <Chip
                        icon={sr.timeliness.within_sla ? <CheckCircleIcon /> : <WarningIcon />}
                        label={sr.timeliness.within_sla ? 'On Time' : 'Delayed'}
                        size="small"
                        color={sr.timeliness.within_sla ? 'success' : 'warning'}
                        variant="outlined"
                      />
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {/* Ingestion Stats */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <PlaylistAddCheckIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Ingestion Results
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Sample Size</Typography>
                            <Typography variant="body2" fontWeight={600}>{sr.sample_size}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Valid Records</Typography>
                            <Typography variant="body2" fontWeight={600} color="success.main">{sr.valid_records}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Errors</Typography>
                            <Typography variant="body2" fontWeight={600} color={sr.error_count > 0 ? 'error.main' : 'text.primary'}>
                              {sr.error_count}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Warnings</Typography>
                            <Typography variant="body2" fontWeight={600} color={sr.warning_count > 0 ? 'warning.main' : 'text.primary'}>
                              {sr.warning_count}
                            </Typography>
                          </Grid>
                        </Grid>
                      </Paper>
                    </Grid>
                    {/* Timeliness */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <ScheduleIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Timeliness
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Frequency</Typography>
                            <Typography variant="body2" fontWeight={600}>{sr.timeliness.frequency}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Expected Max Delay</Typography>
                            <Typography variant="body2" fontWeight={600}>{sr.timeliness.expected_max_delay}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Measured Delay</Typography>
                            <Typography variant="body2" fontWeight={600}>{sr.timeliness.measured_delay}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Within SLA</Typography>
                            <Box display="flex" alignItems="center" gap={0.5}>
                              {sr.timeliness.within_sla
                                ? <><CheckCircleIcon color="success" sx={{ fontSize: 16 }} /><Typography variant="body2" color="success.main" fontWeight={600}>Yes</Typography></>
                                : <><ErrorIcon color="error" sx={{ fontSize: 16 }} /><Typography variant="body2" color="error.main" fontWeight={600}>No</Typography></>}
                            </Box>
                          </Grid>
                          <Grid item xs={12}>
                            <Typography variant="caption" color="text.secondary">{sr.timeliness.detail}</Typography>
                          </Grid>
                        </Grid>
                      </Paper>
                    </Grid>
                    {/* Errors list */}
                    {sr.errors.length > 0 && (
                      <Grid item xs={12}>
                        <Alert severity="error" variant="outlined">
                          <Typography variant="subtitle2" fontWeight={700} mb={0.5}>Ingestion Errors ({sr.error_count} total)</Typography>
                          {sr.errors.map((e, i) => (
                            <Typography key={i} variant="body2" fontFamily="monospace" fontSize={12}>
                              [{e.record_id}] {e.error}
                            </Typography>
                          ))}
                          {sr.error_count > sr.errors.length && (
                            <Typography variant="caption" color="text.secondary" mt={0.5}>
                              ... and {sr.error_count - sr.errors.length} more
                            </Typography>
                          )}
                        </Alert>
                      </Grid>
                    )}
                    {/* Warnings list */}
                    {sr.warnings.length > 0 && (
                      <Grid item xs={12}>
                        <Alert severity="warning" variant="outlined">
                          <Typography variant="subtitle2" fontWeight={700} mb={0.5}>Warnings ({sr.warning_count} total)</Typography>
                          {sr.warnings.map((w, i) => (
                            <Typography key={i} variant="body2" fontFamily="monospace" fontSize={12}>
                              [{w.record_id}] {w.warning}
                            </Typography>
                          ))}
                          {sr.warning_count > sr.warnings.length && (
                            <Typography variant="caption" color="text.secondary" mt={0.5}>
                              ... and {sr.warning_count - sr.warnings.length} more
                            </Typography>
                          )}
                        </Alert>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })}
        </>
      )}
    </>
  );
}

const LIST_TYPE_COLORS = {
  Sanctions: '#b71c1c',
  PEP: '#e65100',
  'Adverse Media': '#4a148c',
};

const formatLag = (s) => {
  if (s < 60) return `${s}s`;
  if (s < 3600) return `${Math.round(s / 60)}m`;
  if (s < 86400) return `${(s / 3600).toFixed(1)}h`;
  return `${(s / 86400).toFixed(1)}d`;
};

function ExternalFeedsTab({ feedResults, feedsLoading, setFeedResults, setFeedsLoading }) {
  const [expandedFeed, setExpandedFeed] = useState(null);

  useEffect(() => {
    if (!feedResults && !feedsLoading) {
      setFeedsLoading(true);
      verifyExternalFeeds()
        .then((res) => setFeedResults(res.data))
        .catch(() => setFeedResults(null))
        .finally(() => setFeedsLoading(false));
    }
  }, [feedResults, feedsLoading, setFeedResults, setFeedsLoading]);

  if (feedsLoading || !feedResults) {
    return (
      <Box display="flex" justifyContent="center" py={6}>
        <CircularProgress />
      </Box>
    );
  }

  const r = feedResults;

  return (
    <>
      {/* Overall banner */}
      <Alert
        severity={r.all_feeds_pass ? 'success' : 'warning'}
        icon={r.all_feeds_pass ? <CheckCircleIcon /> : <WarningIcon />}
        sx={{ mb: 2 }}
      >
        {r.all_feeds_pass
          ? `All ${r.total_feeds} external feeds are up-to-date, format-compatible, and ingested correctly.`
          : `${r.passed} of ${r.total_feeds} feeds passed verification. ${r.failed} feed(s) need attention.`}
      </Alert>

      {/* Summary cards */}
      <Grid container spacing={2} mb={3}>
        {r.feed_results.map((f) => {
          const ltColor = LIST_TYPE_COLORS[f.list_type] || '#263238';
          return (
            <Grid item xs={12} sm={6} md={3} key={f.source_id}>
              <Card variant="outlined" sx={{ borderLeft: `4px solid ${ltColor}` }}>
                <CardContent sx={{ py: 1.5 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                    <Typography variant="subtitle2" fontWeight={700}>{f.feed_name}</Typography>
                    {f.feed_pass
                      ? <CheckCircleIcon color="success" sx={{ fontSize: 20 }} />
                      : <ErrorIcon color="error" sx={{ fontSize: 20 }} />}
                  </Box>
                  <Chip label={f.list_type} size="small" sx={{ bgcolor: ltColor, color: '#fff', mb: 1 }} />
                  <Box display="flex" justifyContent="space-between" mt={0.5}>
                    <Typography variant="caption" color="text.secondary">Active entries</Typography>
                    <Typography variant="caption" fontWeight={600}>{f.active_entries.toLocaleString()}</Typography>
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="caption" color="text.secondary">Format</Typography>
                    <Chip label={f.active_format} size="small" variant="outlined" sx={{ height: 18, fontSize: 11 }} />
                  </Box>
                  <Box display="flex" justifyContent="space-between">
                    <Typography variant="caption" color="text.secondary">Ingestion lag</Typography>
                    <Typography variant="caption" fontWeight={600} color={f.within_acceptable_lag ? 'success.main' : 'error.main'}>
                      {formatLag(f.ingestion_lag_seconds)}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          );
        })}
      </Grid>

      {/* Detailed per-feed accordions */}
      {r.feed_results.map((f) => (
        <Accordion
          key={f.source_id}
          expanded={expandedFeed === f.source_id}
          onChange={() => setExpandedFeed(expandedFeed === f.source_id ? null : f.source_id)}
          sx={{ mb: 1 }}
        >
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" justifyContent="space-between" width="100%" pr={1}>
              <Box display="flex" alignItems="center" gap={1.5}>
                {f.feed_pass ? <CheckCircleIcon color="success" /> : <ErrorIcon color="error" />}
                <Box>
                  <Typography fontWeight={600}>{f.feed_name}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {f.source_id} &bull; {f.provider}
                  </Typography>
                </Box>
              </Box>
              <Box display="flex" alignItems="center" gap={1.5}>
                <Chip label={f.list_type} size="small" color="default" variant="outlined" />
                <Chip
                  icon={f.format_compatible ? <CheckCircleIcon /> : <ErrorIcon />}
                  label={f.active_format}
                  size="small"
                  color={f.format_compatible ? 'success' : 'error'}
                  variant="outlined"
                />
                <Chip
                  icon={f.checksum_verified ? <CheckCircleIcon /> : <ErrorIcon />}
                  label={f.checksum_verified ? 'Integrity OK' : 'Checksum Fail'}
                  size="small"
                  color={f.checksum_verified ? 'success' : 'error'}
                  variant="outlined"
                />
              </Box>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              {/* Feed Identity */}
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={700} mb={1}>
                    <GppGoodIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                    Feed Identity
                  </Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">Provider</Typography>
                      <Typography variant="body2" fontWeight={600}>{f.provider}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">List Type</Typography>
                      <Typography variant="body2" fontWeight={600}>{f.list_type}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Schema Version</Typography>
                      <Typography variant="body2" fontFamily="monospace" fontWeight={600}>{f.schema_version}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">Regulatory Mandate</Typography>
                      <Typography variant="body2">{f.regulatory_mandate}</Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>

              {/* Format & Compatibility */}
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={700} mb={1}>
                    <StorageIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                    Format &amp; Compatibility
                  </Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Active Format</Typography>
                      <Box display="flex" alignItems="center" gap={0.5}>
                        <Chip label={f.active_format} size="small" color="primary" sx={{ height: 20 }} />
                        {f.format_compatible
                          ? <CheckCircleIcon color="success" sx={{ fontSize: 16 }} />
                          : <ErrorIcon color="error" sx={{ fontSize: 16 }} />}
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Supported Formats</Typography>
                      <Box display="flex" gap={0.5} flexWrap="wrap">
                        {f.supported_formats.map((fmt) => (
                          <Chip key={fmt} label={fmt} size="small" variant="outlined" sx={{ height: 20, fontSize: 11 }} />
                        ))}
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">Feed Description</Typography>
                      <Typography variant="body2" fontSize={12}>{f.feed_format}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">Endpoint</Typography>
                      <Typography variant="body2" fontFamily="monospace" fontSize={12} sx={{ bgcolor: 'grey.100', p: 0.5, borderRadius: 1, wordBreak: 'break-all' }}>
                        {f.connection_endpoint}
                      </Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>

              {/* Freshness & Update */}
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={700} mb={1}>
                    <ScheduleIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                    Freshness &amp; Update
                  </Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Last Publisher Update</Typography>
                      <Typography variant="body2" fontWeight={600}>{new Date(f.last_publisher_update).toLocaleString()}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Last Ingested</Typography>
                      <Typography variant="body2" fontWeight={600}>{new Date(f.last_ingested).toLocaleString()}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Ingestion Lag</Typography>
                      <Typography variant="body2" fontWeight={600} color={f.within_acceptable_lag ? 'success.main' : 'error.main'}>
                        {formatLag(f.ingestion_lag_seconds)} (max {formatLag(f.max_acceptable_lag_seconds)})
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Update Schedule</Typography>
                      <Typography variant="body2" fontWeight={600}>{f.update_interval_display}</Typography>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="caption" color="text.secondary">Delta Since Last Ingestion</Typography>
                      <Box display="flex" gap={1} mt={0.5}>
                        <Chip label={`+${f.delta_since_last.added} added`} size="small" color="success" variant="outlined" sx={{ height: 20, fontSize: 11 }} />
                        <Chip label={`~${f.delta_since_last.modified} modified`} size="small" color="info" variant="outlined" sx={{ height: 20, fontSize: 11 }} />
                        <Chip label={`-${f.delta_since_last.removed} removed`} size="small" color="error" variant="outlined" sx={{ height: 20, fontSize: 11 }} />
                      </Box>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>

              {/* Integrity & Volume */}
              <Grid item xs={12} md={6}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={700} mb={1}>
                    <VerifiedUserIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                    Integrity &amp; Volume
                  </Typography>
                  <Grid container spacing={1}>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Total Entries</Typography>
                      <Typography variant="body2" fontWeight={600}>{f.total_entries.toLocaleString()}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Active Entries</Typography>
                      <Typography variant="body2" fontWeight={600}>{f.active_entries.toLocaleString()}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Records Ingested</Typography>
                      <Typography variant="body2" fontWeight={600}>{f.records_ingested_last.toLocaleString()}</Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Records Failed</Typography>
                      <Typography variant="body2" fontWeight={600} color={f.records_failed > 0 ? 'error.main' : 'success.main'}>
                        {f.records_failed}
                      </Typography>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Checksum (SHA-256)</Typography>
                      <Box display="flex" alignItems="center" gap={0.5}>
                        {f.checksum_verified
                          ? <CheckCircleIcon color="success" sx={{ fontSize: 14 }} />
                          : <ErrorIcon color="error" sx={{ fontSize: 14 }} />}
                        <Typography variant="body2" fontFamily="monospace" fontSize={11}>
                          {f.checksum_sha256.substring(0, 16)}...
                        </Typography>
                      </Box>
                    </Grid>
                    <Grid item xs={6}>
                      <Typography variant="caption" color="text.secondary">Coverage</Typography>
                      <Typography variant="body2" fontWeight={600}>{f.coverage_regions.join(', ')}</Typography>
                    </Grid>
                  </Grid>
                </Paper>
              </Grid>

              {/* Data Coverage flags */}
              <Grid item xs={12}>
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle2" fontWeight={700} mb={1}>
                    Data Coverage
                  </Typography>
                  <Box display="flex" gap={1} flexWrap="wrap">
                    <Chip label="Aliases" size="small" color={f.includes_aliases ? 'success' : 'default'} variant={f.includes_aliases ? 'filled' : 'outlined'} />
                    <Chip label="Addresses" size="small" color={f.includes_addresses ? 'success' : 'default'} variant={f.includes_addresses ? 'filled' : 'outlined'} />
                    <Chip label="ID Documents" size="small" color={f.includes_id_documents ? 'success' : 'default'} variant={f.includes_id_documents ? 'filled' : 'outlined'} />
                    <Chip label="Vessels" size="small" color={f.includes_vessels ? 'success' : 'default'} variant={f.includes_vessels ? 'filled' : 'outlined'} />
                  </Box>
                </Paper>
              </Grid>

              {/* Parse errors */}
              {f.parse_errors.length > 0 && (
                <Grid item xs={12}>
                  <Alert severity="error">
                    <strong>Parse Errors:</strong> {f.parse_errors.join('; ')}
                  </Alert>
                </Grid>
              )}
              {f.records_failed > 0 && (
                <Grid item xs={12}>
                  <Alert severity="error">
                    {f.records_failed} records failed to ingest during last update.
                  </Alert>
                </Grid>
              )}
            </Grid>
          </AccordionDetails>
        </Accordion>
      ))}
    </>
  );
}

const STAGE_ICONS = {
  Ingestion: <StorageIcon sx={{ fontSize: 18 }} />,
  Enrichment: <AccountTreeIcon sx={{ fontSize: 18 }} />,
  'Rule Engine': <PlaylistAddCheckIcon sx={{ fontSize: 18 }} />,
  'Alert Generation': <WarningIcon sx={{ fontSize: 18 }} />,
};

const PRIORITY_COLORS = {
  critical: { bg: '#b71c1c', label: 'CRITICAL' },
  high: { bg: '#e65100', label: 'HIGH' },
  medium: { bg: '#f9a825', label: 'MEDIUM' },
  low: { bg: '#2e7d32', label: 'LOW' },
};

function PipelineTestTab({ pipelineResults, pipelineRunning, setPipelineResults, setPipelineRunning }) {
  const [expandedScenario, setExpandedScenario] = useState(null);

  const handleRun = async () => {
    setPipelineRunning(true);
    try {
      const res = await runTestPipeline();
      setPipelineResults(res.data);
    } catch {
      setPipelineResults(null);
    } finally {
      setPipelineRunning(false);
    }
  };

  const r = pipelineResults;

  return (
    <>
      {/* Action bar */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <Box>
          <Typography variant="subtitle1" fontWeight={700}>
            End-to-End Pipeline Test
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Inject {r ? r.total_scenarios : 5} sample transactions with known risk patterns and trace through
            Ingestion &rarr; Enrichment &rarr; Rule Engine &rarr; Alert Generation.
          </Typography>
        </Box>
        <Button
          variant="contained"
          color="secondary"
          startIcon={pipelineRunning ? <CircularProgress size={18} color="inherit" /> : <RocketLaunchIcon />}
          onClick={handleRun}
          disabled={pipelineRunning}
        >
          {pipelineRunning ? 'Running...' : 'Run Pipeline Test'}
        </Button>
      </Paper>

      {!r && !pipelineRunning && (
        <Alert severity="info" sx={{ mb: 2 }}>
          Click <strong>Run Pipeline Test</strong> to inject 5 risk-pattern transactions and verify the full
          Ingestion &rarr; Enrichment &rarr; Rules &rarr; Alert pipeline.
        </Alert>
      )}

      {pipelineRunning && (
        <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>
      )}

      {r && !pipelineRunning && (
        <>
          {/* Summary cards */}
          <Grid container spacing={2} mb={3}>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Scenarios</Typography>
                  <Typography variant="h5" fontWeight={700}>{r.total_scenarios}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Passed</Typography>
                  <Typography variant="h5" fontWeight={700} color="success.main">{r.passed}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Failed</Typography>
                  <Typography variant="h5" fontWeight={700} color={r.failed > 0 ? 'error.main' : 'text.primary'}>{r.failed}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined">
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Avg Latency</Typography>
                  <Typography variant="h5" fontWeight={700}>{r.avg_pipeline_latency_ms}ms</Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Overall banner */}
          <Alert
            severity={r.all_pipeline_pass ? 'success' : 'error'}
            icon={r.all_pipeline_pass ? <CheckCircleIcon /> : <ErrorIcon />}
            sx={{ mb: 2 }}
          >
            {r.all_pipeline_pass
              ? `Complete pipeline verified — all ${r.total_scenarios} scenarios passed from Ingestion → Enrichment → Rules → Alert.`
              : `${r.passed} of ${r.total_scenarios} scenarios passed. ${r.failed} failed — review details below.`}
          </Alert>

          {/* Per-scenario */}
          {r.scenario_results.map((sr) => {
            const prioConf = PRIORITY_COLORS[sr.stages[3]?.alert?.priority] || PRIORITY_COLORS.medium;
            const alertData = sr.stages[3]?.alert;
            return (
              <Accordion
                key={sr.scenario_id}
                expanded={expandedScenario === sr.scenario_id}
                onChange={() => setExpandedScenario(expandedScenario === sr.scenario_id ? null : sr.scenario_id)}
                sx={{ mb: 1 }}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" justifyContent="space-between" width="100%" pr={1}>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      {sr.pipeline_pass ? <CheckCircleIcon color="success" /> : <ErrorIcon color="error" />}
                      <Box>
                        <Typography fontWeight={600}>{sr.title}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {sr.scenario_id} &bull; {sr.risk_pattern}
                        </Typography>
                      </Box>
                    </Box>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      {/* Mini pipeline indicator */}
                      {sr.stages.map((st, i) => (
                        <React.Fragment key={st.stage}>
                          <Tooltip title={`${st.stage}: ${st.status} (${st.latency_ms}ms)`}>
                            <Chip
                              icon={STAGE_ICONS[st.stage]}
                              label={`${st.latency_ms}ms`}
                              size="small"
                              color={st.status === 'passed' ? 'success' : 'error'}
                              variant="outlined"
                              sx={{ fontSize: 11 }}
                            />
                          </Tooltip>
                          {i < sr.stages.length - 1 && <ArrowForwardIcon sx={{ fontSize: 14, color: 'text.disabled' }} />}
                        </React.Fragment>
                      ))}
                      {alertData && (
                        <Chip
                          label={prioConf.label}
                          size="small"
                          sx={{ bgcolor: prioConf.bg, color: '#fff', fontWeight: 700, ml: 1 }}
                        />
                      )}
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {/* Transaction Details */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <StorageIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Transaction
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Transaction ID</Typography>
                            <Typography variant="body2" fontFamily="monospace" fontWeight={600} fontSize={12}>{sr.transaction.transaction_id}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Source</Typography>
                            <Typography variant="body2" fontWeight={600}>{sr.transaction.source_name}</Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Amount</Typography>
                            <Typography variant="body2" fontWeight={700} color="primary.main">
                              ${sr.transaction.amount?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                            </Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Currency</Typography>
                            <Typography variant="body2" fontWeight={600}>{sr.transaction.currency}</Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Country</Typography>
                            <Typography variant="body2" fontWeight={600}>{sr.transaction.geo_country}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Customer</Typography>
                            <Typography variant="body2" fontWeight={600}>{sr.transaction.customer_name}</Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography variant="caption" color="text.secondary">Channel</Typography>
                            <Chip label={sr.transaction.channel} size="small" variant="outlined" sx={{ height: 20 }} />
                          </Grid>
                        </Grid>
                      </Paper>
                    </Grid>

                    {/* Pipeline Stages */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <RocketLaunchIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Pipeline Stages ({sr.pipeline_latency_ms}ms total)
                        </Typography>
                        {sr.stages.map((st) => (
                          <Box key={st.stage} display="flex" alignItems="center" gap={1} mb={0.75}>
                            {st.status === 'passed'
                              ? <CheckCircleIcon color="success" sx={{ fontSize: 18 }} />
                              : <ErrorIcon color="error" sx={{ fontSize: 18 }} />}
                            <Typography variant="body2" fontWeight={600} sx={{ minWidth: 130 }}>{st.stage}</Typography>
                            <Chip label={`${st.latency_ms}ms`} size="small" variant="outlined" sx={{ height: 20, fontSize: 11 }} />
                            <Typography variant="caption" color="text.secondary" sx={{ flex: 1 }}>{st.detail}</Typography>
                          </Box>
                        ))}
                      </Paper>
                    </Grid>

                    {/* Enrichment Details */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <AccountTreeIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Enrichment ({Object.keys(sr.stages[1]?.enrichments || {}).length} attributes)
                        </Typography>
                        <TableContainer>
                          <Table size="small">
                            <TableHead>
                              <TableRow sx={{ bgcolor: 'grey.50' }}>
                                <TableCell sx={{ fontWeight: 700, py: 0.5 }}>Attribute</TableCell>
                                <TableCell sx={{ fontWeight: 700, py: 0.5 }}>Value</TableCell>
                                <TableCell sx={{ fontWeight: 700, py: 0.5 }}>Source</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {Object.entries(sr.stages[1]?.enrichments || {}).map(([key, val]) => (
                                <TableRow key={key}>
                                  <TableCell sx={{ py: 0.5 }}>
                                    <Typography variant="body2" fontFamily="monospace" fontSize={12}>{key}</Typography>
                                  </TableCell>
                                  <TableCell sx={{ py: 0.5 }}>
                                    <Typography variant="body2" fontSize={12}>{val.value}</Typography>
                                  </TableCell>
                                  <TableCell sx={{ py: 0.5 }}>
                                    <Typography variant="caption" color="text.secondary">{val.source}</Typography>
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </Paper>
                    </Grid>

                    {/* Rules + Alert */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <PlaylistAddCheckIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Rules Fired ({sr.stages[2]?.rules_fired?.length || 0})
                        </Typography>
                        {(sr.stages[2]?.rules_fired || []).map((rule) => (
                          <Box key={rule.rule_id} display="flex" alignItems="center" gap={1} mb={0.5}>
                            <Chip label={rule.rule_id} size="small" color="warning" variant="outlined" sx={{ fontFamily: 'monospace', fontSize: 11, height: 22 }} />
                            <Typography variant="body2" fontSize={12} sx={{ flex: 1 }}>{rule.rule_name}</Typography>
                            <Chip label={`+${rule.score_contribution}`} size="small" sx={{ height: 20, fontSize: 11, bgcolor: '#fff3e0' }} />
                          </Box>
                        ))}
                        <Divider sx={{ my: 1.5 }} />
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <WarningIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom', color: prioConf.bg }} />
                          Alert Generated
                        </Typography>
                        {alertData && (
                          <Grid container spacing={1}>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="text.secondary">Alert ID</Typography>
                              <Typography variant="body2" fontFamily="monospace" fontWeight={600} fontSize={12}>{alertData.alert_id}</Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="text.secondary">Priority</Typography>
                              <Chip label={prioConf.label} size="small" sx={{ bgcolor: prioConf.bg, color: '#fff', fontWeight: 700, height: 22 }} />
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="text.secondary">Risk Score</Typography>
                              <Typography variant="body2" fontWeight={700} color={alertData.risk_score >= 70 ? 'error.main' : 'warning.main'}>
                                {alertData.risk_score}/100
                              </Typography>
                            </Grid>
                            <Grid item xs={6}>
                              <Typography variant="caption" color="text.secondary">Status</Typography>
                              <Chip label="NEW" size="small" color="info" sx={{ height: 20, fontSize: 11 }} />
                            </Grid>
                          </Grid>
                        )}
                      </Paper>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })}
        </>
      )}
    </>
  );
}

const HEALTH_CONFIG = {
  healthy: { color: 'success', icon: <CheckCircleIcon />, label: 'Healthy' },
  warning: { color: 'warning', icon: <WarningIcon />, label: 'Warning' },
  critical: { color: 'error', icon: <ErrorIcon />, label: 'Critical' },
};

function MiniSparkline({ data, color = '#1976d2', height = 32, width = 120 }) {
  const max = Math.max(...data, 1);
  const points = data.map((v, i) => `${(i / (data.length - 1)) * width},${height - (v / max) * height}`).join(' ');
  return (
    <svg width={width} height={height} style={{ display: 'block' }}>
      <polyline fill="none" stroke={color} strokeWidth={1.5} points={points} />
    </svg>
  );
}

function MonitoringTab({ metricsData, metricsLoading, setMetricsData, setMetricsLoading }) {
  const [expandedSource, setExpandedSource] = useState(null);
  const [autoRefresh, setAutoRefresh] = useState(false);

  const loadMetrics = async () => {
    setMetricsLoading(true);
    try {
      const res = await getDataSourceMetrics();
      setMetricsData(res.data);
    } catch {
      setMetricsData(null);
    } finally {
      setMetricsLoading(false);
    }
  };

  useEffect(() => {
    if (!metricsData && !metricsLoading) loadMetrics();
  }, []);

  useEffect(() => {
    if (!autoRefresh) return;
    const id = setInterval(loadMetrics, 30000);
    return () => clearInterval(id);
  }, [autoRefresh]);

  const m = metricsData;

  return (
    <>
      {/* Header bar */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <Box>
          <Typography variant="subtitle1" fontWeight={700}>
            <MonitorHeartIcon sx={{ fontSize: 20, mr: 0.5, verticalAlign: 'text-bottom' }} />
            Data Source Monitoring
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Real-time metrics per source — throughput, ingestion failures, data lag, field quality &amp; threshold alerts.
          </Typography>
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <Tooltip title={autoRefresh ? 'Auto-refresh ON (30 s)' : 'Enable auto-refresh'}>
            <Chip
              icon={<SyncIcon />}
              label={autoRefresh ? 'Auto' : 'Manual'}
              color={autoRefresh ? 'success' : 'default'}
              variant={autoRefresh ? 'filled' : 'outlined'}
              onClick={() => setAutoRefresh(!autoRefresh)}
              size="small"
              sx={{ cursor: 'pointer' }}
            />
          </Tooltip>
          <Button
            variant="contained"
            startIcon={metricsLoading ? <CircularProgress size={18} color="inherit" /> : <RefreshIcon />}
            onClick={loadMetrics}
            disabled={metricsLoading}
            size="small"
          >
            {metricsLoading ? 'Loading...' : 'Refresh'}
          </Button>
        </Box>
      </Paper>

      {metricsLoading && !m && (
        <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>
      )}

      {m && (
        <>
          {/* Summary cards */}
          <Grid container spacing={2} mb={2}>
            <Grid item xs={6} sm={3} md={2}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="caption" color="text.secondary">Sources</Typography>
                <Typography variant="h5" fontWeight={700}>{m.summary.total_sources}</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={6} sm={3} md={2}>
              <Card variant="outlined" sx={{ borderColor: 'success.main' }}><CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="caption" color="text.secondary">Healthy</Typography>
                <Typography variant="h5" fontWeight={700} color="success.main">{m.summary.healthy}</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={6} sm={3} md={2}>
              <Card variant="outlined" sx={{ borderColor: m.summary.warning > 0 ? 'warning.main' : undefined }}>
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Warning</Typography>
                  <Typography variant="h5" fontWeight={700} color={m.summary.warning > 0 ? 'warning.main' : 'text.primary'}>{m.summary.warning}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3} md={2}>
              <Card variant="outlined" sx={{ borderColor: m.summary.critical > 0 ? 'error.main' : undefined }}>
                <CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                  <Typography variant="caption" color="text.secondary">Critical</Typography>
                  <Typography variant="h5" fontWeight={700} color={m.summary.critical > 0 ? 'error.main' : 'text.primary'}>{m.summary.critical}</Typography>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={6} sm={3} md={2}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="caption" color="text.secondary">Avg Success Rate</Typography>
                <Typography variant="h5" fontWeight={700}>{m.summary.avg_success_rate}%</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={6} sm={3} md={2}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="caption" color="text.secondary">Total Txns (24 h)</Typography>
                <Typography variant="h5" fontWeight={700}>{(m.summary.total_transactions_24h / 1e6).toFixed(1)}M</Typography>
              </CardContent></Card>
            </Grid>
          </Grid>

          {/* Alerts banner */}
          {m.summary.total_alerts > 0 && (
            <Alert
              severity={m.summary.critical_alerts > 0 ? 'error' : 'warning'}
              icon={<NotificationsActiveIcon />}
              sx={{ mb: 2 }}
            >
              <strong>{m.summary.total_alerts} active alert{m.summary.total_alerts > 1 ? 's' : ''}:</strong>{' '}
              {m.summary.critical_alerts > 0 && `${m.summary.critical_alerts} critical`}
              {m.summary.critical_alerts > 0 && m.summary.warning_alerts > 0 && ', '}
              {m.summary.warning_alerts > 0 && `${m.summary.warning_alerts} warning`}
              {' '}— review sources below for details.
            </Alert>
          )}
          {m.summary.total_alerts === 0 && (
            <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 2 }}>
              <strong>All {m.summary.total_sources} sources within thresholds.</strong> Continuous monitoring active — no alerts triggered.
            </Alert>
          )}

          {/* Threshold reference */}
          <Paper variant="outlined" sx={{ p: 1.5, mb: 3, bgcolor: 'grey.50' }}>
            <Typography variant="caption" fontWeight={700} sx={{ mr: 2 }}>
              Alert Thresholds:
            </Typography>
            {Object.values(m.thresholds).map((t) => (
              <Chip
                key={t.label}
                label={`${t.label}: warn ≥ ${t.warn}${typeof t.warn === 'number' && t.warn < 10 ? '%' : ''} · crit ≥ ${t.critical}${typeof t.critical === 'number' && t.critical < 10 ? '%' : ''}`}
                size="small"
                variant="outlined"
                sx={{ mr: 1, mb: 0.5, fontSize: 11 }}
              />
            ))}
          </Paper>

          {/* Per-source accordions */}
          {m.sources.map((src) => {
            const hc = HEALTH_CONFIG[src.health] || HEALTH_CONFIG.healthy;
            return (
              <Accordion
                key={src.source_id}
                expanded={expandedSource === src.source_id}
                onChange={() => setExpandedSource(expandedSource === src.source_id ? null : src.source_id)}
                sx={{ mb: 1 }}
              >
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" justifyContent="space-between" width="100%" pr={1}>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      {React.cloneElement(hc.icon, { color: hc.color, sx: { fontSize: 22 } })}
                      <Box>
                        <Typography fontWeight={600} fontSize={14}>{src.source_name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {src.source_id} &bull; {src.category}
                        </Typography>
                      </Box>
                    </Box>
                    <Box display="flex" alignItems="center" gap={1.5}>
                      <Tooltip title="Transactions / min">
                        <Chip icon={<TrendingUpIcon />} label={`${src.throughput.transactions_per_minute} tpm`} size="small" variant="outlined" sx={{ fontSize: 11 }} />
                      </Tooltip>
                      <Tooltip title="Failed ingestion %">
                        <Chip
                          label={`${src.ingestion.failed_pct}% fail`}
                          size="small"
                          color={src.ingestion.failed_pct >= 5 ? 'error' : src.ingestion.failed_pct >= 2 ? 'warning' : 'success'}
                          variant="outlined"
                          sx={{ fontSize: 11 }}
                        />
                      </Tooltip>
                      <Tooltip title="Data lag">
                        <Chip
                          icon={<ScheduleIcon />}
                          label={`${src.data_lag.current_seconds}s lag`}
                          size="small"
                          color={src.data_lag.within_sla ? 'success' : 'error'}
                          variant="outlined"
                          sx={{ fontSize: 11 }}
                        />
                      </Tooltip>
                      {src.alerts.length > 0 && (
                        <Chip
                          icon={<NotificationsActiveIcon />}
                          label={`${src.alerts.length} alert${src.alerts.length > 1 ? 's' : ''}`}
                          size="small"
                          color={src.alerts.some(a => a.severity === 'critical') ? 'error' : 'warning'}
                          sx={{ fontSize: 11, fontWeight: 700 }}
                        />
                      )}
                    </Box>
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {/* Throughput */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <TrendingUpIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Throughput
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Txns / min</Typography>
                            <Typography variant="h6" fontWeight={700}>{src.throughput.transactions_per_minute.toLocaleString()}</Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Txns / hour</Typography>
                            <Typography variant="h6" fontWeight={700}>{src.throughput.transactions_per_hour.toLocaleString()}</Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">24 h total</Typography>
                            <Typography variant="h6" fontWeight={700}>{src.throughput.transactions_24h.toLocaleString()}</Typography>
                          </Grid>
                        </Grid>
                        <Box mt={1}>
                          <Typography variant="caption" color="text.secondary">Hourly volume (24 h)</Typography>
                          <MiniSparkline data={src.throughput.sparkline_hourly} width={320} height={36} />
                        </Box>
                        <Box display="flex" alignItems="center" gap={1} mt={0.5}>
                          <Typography variant="caption" color="text.secondary">Variance from avg:</Typography>
                          <Chip
                            label={`${src.throughput.variance_pct}%`}
                            size="small"
                            color={src.throughput.variance_pct >= 40 ? 'error' : src.throughput.variance_pct >= 20 ? 'warning' : 'success'}
                            sx={{ height: 20, fontSize: 11 }}
                          />
                        </Box>
                      </Paper>
                    </Grid>

                    {/* Ingestion */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <StorageIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Ingestion (24 h)
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Total Attempts</Typography>
                            <Typography variant="body1" fontWeight={700}>{src.ingestion.total_attempts_24h.toLocaleString()}</Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Successful</Typography>
                            <Typography variant="body1" fontWeight={700} color="success.main">{src.ingestion.successful.toLocaleString()}</Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Failed</Typography>
                            <Typography variant="body1" fontWeight={700} color={src.ingestion.failed > 0 ? 'error.main' : 'text.primary'}>{src.ingestion.failed.toLocaleString()}</Typography>
                          </Grid>
                        </Grid>
                        <Box mt={1.5}>
                          <Box display="flex" justifyContent="space-between" mb={0.5}>
                            <Typography variant="caption">Success rate</Typography>
                            <Typography variant="caption" fontWeight={700}>{src.ingestion.success_rate}%</Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={src.ingestion.success_rate}
                            color={src.ingestion.failed_pct >= 5 ? 'error' : src.ingestion.failed_pct >= 2 ? 'warning' : 'success'}
                            sx={{ height: 8, borderRadius: 4 }}
                          />
                        </Box>
                        <Box display="flex" alignItems="center" gap={1} mt={1}>
                          <Typography variant="caption" color="text.secondary">Failed %:</Typography>
                          <Chip
                            label={`${src.ingestion.failed_pct}%`}
                            size="small"
                            color={src.ingestion.failed_pct >= 5 ? 'error' : src.ingestion.failed_pct >= 2 ? 'warning' : 'success'}
                            sx={{ height: 20, fontSize: 11, fontWeight: 700 }}
                          />
                          {src.ingestion.failed_pct >= 5 && (
                            <Typography variant="caption" color="error.main" fontWeight={700}>
                              THRESHOLD EXCEEDED (&gt;5%)
                            </Typography>
                          )}
                        </Box>
                      </Paper>
                    </Grid>

                    {/* Data Lag */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <ScheduleIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Data Lag
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={3}>
                            <Typography variant="caption" color="text.secondary">Current</Typography>
                            <Typography variant="body1" fontWeight={700} color={src.data_lag.within_sla ? 'success.main' : 'error.main'}>
                              {src.data_lag.current_seconds}s
                            </Typography>
                          </Grid>
                          <Grid item xs={3}>
                            <Typography variant="caption" color="text.secondary">Average</Typography>
                            <Typography variant="body1" fontWeight={700}>{src.data_lag.avg_seconds}s</Typography>
                          </Grid>
                          <Grid item xs={3}>
                            <Typography variant="caption" color="text.secondary">P95</Typography>
                            <Typography variant="body1" fontWeight={700}>{src.data_lag.p95_seconds}s</Typography>
                          </Grid>
                          <Grid item xs={3}>
                            <Typography variant="caption" color="text.secondary">SLA Max</Typography>
                            <Typography variant="body1" fontWeight={700}>{src.data_lag.expected_max_seconds}s</Typography>
                          </Grid>
                        </Grid>
                        <Box display="flex" alignItems="center" gap={1} mt={1}>
                          <Typography variant="caption" color="text.secondary">Within SLA:</Typography>
                          {src.data_lag.within_sla
                            ? <Chip icon={<CheckCircleIcon />} label="Yes" size="small" color="success" sx={{ height: 22, fontSize: 11 }} />
                            : <Chip icon={<ErrorIcon />} label="No — exceeds max" size="small" color="error" sx={{ height: 22, fontSize: 11 }} />}
                        </Box>
                      </Paper>
                    </Grid>

                    {/* Data Quality */}
                    <Grid item xs={12} md={6}>
                      <Paper variant="outlined" sx={{ p: 2 }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <PlaylistAddCheckIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          Missing / Null Fields
                        </Typography>
                        <Grid container spacing={1}>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Fields Monitored</Typography>
                            <Typography variant="body1" fontWeight={700}>{src.data_quality.fields_monitored}</Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Total Checks</Typography>
                            <Typography variant="body1" fontWeight={700}>{src.data_quality.total_fields_checked.toLocaleString()}</Typography>
                          </Grid>
                          <Grid item xs={4}>
                            <Typography variant="caption" color="text.secondary">Null / Missing</Typography>
                            <Typography variant="body1" fontWeight={700} color={src.data_quality.null_pct >= 3 ? 'error.main' : 'text.primary'}>
                              {src.data_quality.null_or_missing.toLocaleString()}
                            </Typography>
                          </Grid>
                        </Grid>
                        <Box display="flex" alignItems="center" gap={1} mt={1}>
                          <Typography variant="caption" color="text.secondary">Null %:</Typography>
                          <Chip
                            label={`${src.data_quality.null_pct}%`}
                            size="small"
                            color={src.data_quality.null_pct >= 3 ? 'error' : src.data_quality.null_pct >= 1 ? 'warning' : 'success'}
                            sx={{ height: 20, fontSize: 11, fontWeight: 700 }}
                          />
                        </Box>
                      </Paper>
                    </Grid>

                    {/* Alerts for this source */}
                    {src.alerts.length > 0 && (
                      <Grid item xs={12}>
                        <Paper variant="outlined" sx={{ p: 2, borderColor: src.alerts.some(a => a.severity === 'critical') ? 'error.main' : 'warning.main' }}>
                          <Typography variant="subtitle2" fontWeight={700} mb={1}>
                            <NotificationsActiveIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom', color: 'error.main' }} />
                            Active Alerts ({src.alerts.length})
                          </Typography>
                          {src.alerts.map((al, idx) => (
                            <Alert key={idx} severity={al.severity === 'critical' ? 'error' : 'warning'} sx={{ mb: 0.5, py: 0 }}>
                              <Typography variant="body2" fontSize={13}>
                                <strong>{al.label}:</strong> {al.message}
                              </Typography>
                            </Alert>
                          ))}
                        </Paper>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })}
        </>
      )}
    </>
  );
}

const ACTION_COLORS = {
  CONFIG_CHANGE: 'info',
  FEED_UPDATE: 'success',
  THRESHOLD_ALERT: 'warning',
  SOURCE_ADDED: 'primary',
  CERT_ROTATION: 'secondary',
  AUTH_CHANGE: 'info',
  SCHEMA_CHANGE: 'primary',
  AUTOMATED_HEALTH_CHECK: 'default',
  CREDENTIAL_ROTATION_CHECK: 'default',
};

function DocumentationTab({ inventoryData, inventoryLoading, setInventoryData, setInventoryLoading }) {
  const [expandedSource, setExpandedSource] = useState(null);
  const [section, setSection] = useState('inventory');

  const load = async () => {
    setInventoryLoading(true);
    try {
      const res = await getDataSourceInventory();
      setInventoryData(res.data);
    } catch {
      setInventoryData(null);
    } finally {
      setInventoryLoading(false);
    }
  };

  useEffect(() => {
    if (!inventoryData && !inventoryLoading) load();
  }, []);

  const d = inventoryData;
  if (inventoryLoading && !d) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>;
  if (!d) return <Alert severity="error">Failed to load inventory.</Alert>;

  return (
    <>
      {/* Header */}
      <Paper sx={{ p: 2, mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap' }}>
        <Box>
          <Typography variant="subtitle1" fontWeight={700}>
            <DescriptionIcon sx={{ fontSize: 20, mr: 0.5, verticalAlign: 'text-bottom' }} />
            {d.document_title}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Revision {d.revision} &bull; Last reviewed {d.last_reviewed} &bull; {d.total_sources} sources across {d.categories.length} categories
          </Typography>
        </Box>
        <Button
          variant="contained"
          startIcon={inventoryLoading ? <CircularProgress size={18} color="inherit" /> : <RefreshIcon />}
          onClick={load}
          disabled={inventoryLoading}
          size="small"
        >
          Refresh
        </Button>
      </Paper>

      {/* Section selector */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={section} onChange={(_, v) => setSection(v)} variant="fullWidth">
          <Tab value="inventory" icon={<StorageIcon />} iconPosition="start" label="Source Inventory" />
          <Tab value="changelog" icon={<HistoryIcon />} iconPosition="start" label={`Config Changelog (${d.config_changelog.length})`} />
          <Tab value="audit" icon={<VerifiedUserIcon />} iconPosition="start" label={`Audit Trail (${d.audit_trail.length})`} />
        </Tabs>
      </Paper>

      {/* ─── INVENTORY ─── */}
      {section === 'inventory' && (
        <>
          {/* Summary cards */}
          <Grid container spacing={2} mb={2}>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="caption" color="text.secondary">Total Sources</Typography>
                <Typography variant="h5" fontWeight={700}>{d.total_sources}</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="caption" color="text.secondary">Categories</Typography>
                <Typography variant="h5" fontWeight={700}>{d.categories.length}</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="caption" color="text.secondary">Current Revision</Typography>
                <Typography variant="h5" fontWeight={700}>{d.revision}</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={6} sm={3}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1.5 }}>
                <Typography variant="caption" color="text.secondary">Last Review</Typography>
                <Typography variant="h5" fontWeight={700}>{d.last_reviewed}</Typography>
              </CardContent></Card>
            </Grid>
          </Grid>

          <Alert severity="success" icon={<CheckCircleIcon />} sx={{ mb: 2 }}>
            <strong>Documentation complete for regulators and internal audits.</strong>{' '}
            All {d.total_sources} data sources inventoried with connection details, AML field mappings, owners, and update schedules.
          </Alert>

          {/* Per-source inventory */}
          {d.inventory.map((src) => (
            <Accordion
              key={src.source_id}
              expanded={expandedSource === src.source_id}
              onChange={() => setExpandedSource(expandedSource === src.source_id ? null : src.source_id)}
              sx={{ mb: 1 }}
            >
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" justifyContent="space-between" width="100%" pr={1}>
                  <Box display="flex" alignItems="center" gap={1.5}>
                    <StorageIcon color="primary" sx={{ fontSize: 22 }} />
                    <Box>
                      <Typography fontWeight={600} fontSize={14}>{src.source_name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {src.source_id} &bull; {src.category}
                      </Typography>
                    </Box>
                  </Box>
                  <Box display="flex" alignItems="center" gap={1}>
                    <Chip label={src.connection.type} size="small" variant="outlined" sx={{ fontSize: 11 }} />
                    <Chip
                      label={src.update_frequency.frequency}
                      size="small"
                      icon={<ScheduleIcon />}
                      variant="outlined"
                      sx={{ fontSize: 11 }}
                    />
                    <Chip
                      label={src.schema_mapping.total_fields_mapped + ' fields'}
                      size="small"
                      icon={<AccountTreeIcon />}
                      variant="outlined"
                      sx={{ fontSize: 11 }}
                    />
                    <Tooltip title={`${src.owner.owner} (${src.owner.team})`}>
                      <Chip
                        label={src.owner.owner.split(' ')[0]}
                        size="small"
                        icon={<PersonIcon />}
                        variant="outlined"
                        sx={{ fontSize: 11 }}
                      />
                    </Tooltip>
                  </Box>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  {/* Source Identity */}
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle2" fontWeight={700} mb={1}>
                        <InfoOutlinedIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                        Source Identity
                      </Typography>
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Source ID</Typography>
                          <Typography variant="body2" fontFamily="monospace" fontWeight={600}>{src.source_id}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Category</Typography>
                          <Typography variant="body2" fontWeight={600}>{src.category}</Typography>
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">Description</Typography>
                          <Typography variant="body2">{src.description}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Status</Typography>
                          <Chip label={src.status} size="small" color={src.status === 'connected' ? 'success' : src.status === 'degraded' ? 'warning' : 'error'} sx={{ height: 22 }} />
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Last Connected</Typography>
                          <Typography variant="body2" fontSize={12}>{src.last_connected || 'N/A'}</Typography>
                        </Grid>
                      </Grid>
                    </Paper>
                  </Grid>

                  {/* Connection Details */}
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle2" fontWeight={700} mb={1}>
                        <LockIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                        Connection Details
                      </Typography>
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Type</Typography>
                          <Typography variant="body2" fontWeight={600}>{src.connection.type}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Class</Typography>
                          <Chip label={src.connection.class} size="small" variant="outlined" sx={{ height: 22, fontSize: 11 }} />
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">Endpoint</Typography>
                          <Typography variant="body2" fontFamily="monospace" fontSize={11} sx={{ wordBreak: 'break-all' }}>{src.connection.endpoint}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Auth Method</Typography>
                          <Typography variant="body2" fontSize={12}>{src.connection.auth_method}</Typography>
                        </Grid>
                        <Grid item xs={3}>
                          <Typography variant="caption" color="text.secondary">Credentials</Typography>
                          {src.connection.credentials_valid
                            ? <Chip icon={<CheckCircleIcon />} label="Valid" size="small" color="success" sx={{ height: 22, fontSize: 11 }} />
                            : <Chip icon={<ErrorIcon />} label="Invalid" size="small" color="error" sx={{ height: 22, fontSize: 11 }} />}
                        </Grid>
                        <Grid item xs={3}>
                          <Typography variant="caption" color="text.secondary">Permission</Typography>
                          <Typography variant="body2" fontSize={12}>{src.connection.permission_level}</Typography>
                        </Grid>
                      </Grid>
                    </Paper>
                  </Grid>

                  {/* AML Field Mapping */}
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle2" fontWeight={700} mb={1}>
                        <AccountTreeIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                        AML Schema Mapping ({src.schema_mapping.total_fields_mapped} fields)
                      </Typography>
                      <Box display="flex" gap={1} mb={1}>
                        <Chip label={`${src.schema_mapping.required_mapped} required`} size="small" color="primary" variant="outlined" sx={{ fontSize: 11 }} />
                        <Chip label={`${src.schema_mapping.optional_mapped} optional`} size="small" variant="outlined" sx={{ fontSize: 11 }} />
                      </Box>
                      {src.schema_mapping.fields.length > 0 ? (
                        <TableContainer sx={{ maxHeight: 180 }}>
                          <Table size="small" stickyHeader>
                            <TableHead>
                              <TableRow sx={{ bgcolor: 'grey.50' }}>
                                <TableCell sx={{ fontWeight: 700, py: 0.5, fontSize: 11 }}>Source Field</TableCell>
                                <TableCell sx={{ fontWeight: 700, py: 0.5, fontSize: 11 }}>AML Field</TableCell>
                                <TableCell sx={{ fontWeight: 700, py: 0.5, fontSize: 11 }}>Req</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {src.schema_mapping.fields.map((f, i) => (
                                <TableRow key={i}>
                                  <TableCell sx={{ py: 0.25, fontFamily: 'monospace', fontSize: 11 }}>{f.source_field}</TableCell>
                                  <TableCell sx={{ py: 0.25, fontFamily: 'monospace', fontSize: 11 }}>{f.aml_field}</TableCell>
                                  <TableCell sx={{ py: 0.25 }}>
                                    {f.required ? <CheckCircleIcon color="primary" sx={{ fontSize: 14 }} /> : <span style={{ color: '#bbb' }}>—</span>}
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      ) : (
                        <Typography variant="body2" color="text.secondary" fontSize={12}>No direct AML mapping (external feed or lookup source).</Typography>
                      )}
                    </Paper>
                  </Grid>

                  {/* Update Frequency & Owner */}
                  <Grid item xs={12} md={6}>
                    <Paper variant="outlined" sx={{ p: 2 }}>
                      <Typography variant="subtitle2" fontWeight={700} mb={1}>
                        <ScheduleIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                        Update Schedule
                      </Typography>
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Frequency</Typography>
                          <Typography variant="body2" fontWeight={600}>{src.update_frequency.frequency}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Interval</Typography>
                          <Typography variant="body2" fontSize={12}>{src.update_frequency.interval_display}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Max Delay SLA</Typography>
                          <Typography variant="body2" fontWeight={600}>{src.update_frequency.expected_max_delay_seconds}s</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Records / Day</Typography>
                          <Typography variant="body2" fontWeight={600}>{src.update_frequency.records_per_day?.toLocaleString()}</Typography>
                        </Grid>
                      </Grid>
                      <Divider sx={{ my: 1.5 }} />
                      <Typography variant="subtitle2" fontWeight={700} mb={1}>
                        <PersonIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                        Responsible Owner
                      </Typography>
                      <Grid container spacing={1}>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Name</Typography>
                          <Typography variant="body2" fontWeight={600}>{src.owner.owner}</Typography>
                        </Grid>
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Team</Typography>
                          <Typography variant="body2" fontWeight={600}>{src.owner.team}</Typography>
                        </Grid>
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">Email</Typography>
                          <Typography variant="body2" fontFamily="monospace" fontSize={12}>{src.owner.email}</Typography>
                        </Grid>
                      </Grid>
                    </Paper>
                  </Grid>

                  {/* External feed info (if applicable) */}
                  {src.external_feed && (
                    <Grid item xs={12}>
                      <Paper variant="outlined" sx={{ p: 2, bgcolor: '#f5f5ff' }}>
                        <Typography variant="subtitle2" fontWeight={700} mb={1}>
                          <GppGoodIcon sx={{ fontSize: 16, mr: 0.5, verticalAlign: 'text-bottom' }} />
                          External Feed Details
                        </Typography>
                        <Box display="flex" gap={2}>
                          <Box>
                            <Typography variant="caption" color="text.secondary">Provider</Typography>
                            <Typography variant="body2" fontWeight={600}>{src.external_feed.provider}</Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.secondary">Regulatory Mandate</Typography>
                            <Typography variant="body2" fontWeight={600}>{src.external_feed.regulatory_mandate}</Typography>
                          </Box>
                          <Box>
                            <Typography variant="caption" color="text.secondary">Format</Typography>
                            <Chip label={src.external_feed.format} size="small" variant="outlined" sx={{ fontSize: 11 }} />
                          </Box>
                        </Box>
                      </Paper>
                    </Grid>
                  )}
                </Grid>
              </AccordionDetails>
            </Accordion>
          ))}
        </>
      )}

      {/* ─── CONFIG CHANGELOG ─── */}
      {section === 'changelog' && (
        <>
          <Alert severity="info" icon={<HistoryIcon />} sx={{ mb: 2 }}>
            Version-controlled configuration change log. All changes require peer review and are tracked for SOX / BSA compliance.
          </Alert>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead>
                <TableRow sx={{ bgcolor: 'grey.50' }}>
                  <TableCell sx={{ fontWeight: 700 }}>Version</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Date</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Author</TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>Change Description</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {d.config_changelog.map((c, i) => (
                  <TableRow key={i} sx={{ bgcolor: i === 0 ? '#e8f5e9' : undefined }}>
                    <TableCell>
                      <Chip label={c.version} size="small" color={i === 0 ? 'success' : 'default'} variant={i === 0 ? 'filled' : 'outlined'} sx={{ fontFamily: 'monospace', fontWeight: 700, fontSize: 12 }} />
                    </TableCell>
                    <TableCell><Typography variant="body2" fontSize={13}>{c.date}</Typography></TableCell>
                    <TableCell><Typography variant="body2" fontFamily="monospace" fontSize={12}>{c.author}</Typography></TableCell>
                    <TableCell><Typography variant="body2" fontSize={13}>{c.change}</Typography></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </>
      )}

      {/* ─── AUDIT TRAIL ─── */}
      {section === 'audit' && (
        <>
          <Alert severity="info" icon={<VerifiedUserIcon />} sx={{ mb: 2 }}>
            Immutable audit trail for regulatory compliance (BSA/AML, SOX, GDPR). All system and operator actions are logged.
          </Alert>
          {d.audit_trail.map((entry, i) => (
            <Paper key={i} variant="outlined" sx={{ p: 1.5, mb: 1, display: 'flex', alignItems: 'flex-start', gap: 1.5, borderLeft: 3, borderLeftColor: entry.action === 'THRESHOLD_ALERT' ? 'warning.main' : 'primary.main' }}>
              <Box sx={{ minWidth: 170 }}>
                <Typography variant="caption" color="text.secondary">Timestamp</Typography>
                <Typography variant="body2" fontFamily="monospace" fontSize={11}>{entry.timestamp}</Typography>
              </Box>
              <Box sx={{ minWidth: 160 }}>
                <Typography variant="caption" color="text.secondary">Actor</Typography>
                <Typography variant="body2" fontFamily="monospace" fontSize={12}>{entry.actor}</Typography>
              </Box>
              <Box sx={{ minWidth: { xs: 80, sm: 140 } }}>
                <Chip
                  label={entry.action.replace(/_/g, ' ')}
                  size="small"
                  color={ACTION_COLORS[entry.action] || 'default'}
                  variant="outlined"
                  sx={{ fontSize: 10, fontWeight: 700 }}
                />
              </Box>
              <Box sx={{ flex: 1 }}>
                <Typography variant="body2" fontSize={13}>{entry.detail}</Typography>
              </Box>
            </Paper>
          ))}
        </>
      )}
    </>
  );
}

/* ═══════════════════ TAB 8 – Key Capabilities ═══════════════════ */
function CapabilitiesTab({ capabilitiesData, capabilitiesLoading, setCapabilitiesData, setCapabilitiesLoading }) {
  const handleRunVerification = async () => {
    setCapabilitiesLoading(true);
    try {
      const res = await verifyCapabilities();
      setCapabilitiesData(res.data);
    } catch (err) {
      setCapabilitiesData({ error: 'Verification request failed' });
    } finally {
      setCapabilitiesLoading(false);
    }
  };

  return (
    <>
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
        <Typography variant="h6"><SecurityIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Key Capabilities Verification</Typography>
        <Button variant="contained" startIcon={<SecurityIcon />} onClick={handleRunVerification} disabled={capabilitiesLoading}>
          {capabilitiesLoading ? <><CircularProgress size={18} sx={{ mr: 1 }} />Running…</> : 'Run Verification'}
        </Button>
      </Box>

      {!capabilitiesData && !capabilitiesLoading && (
        <Alert severity="info" sx={{ mb: 2 }}>Click <strong>Run Verification</strong> to validate all AML/CFT key capabilities across the platform.</Alert>
      )}

      {capabilitiesData && capabilitiesData.error && (
        <Alert severity="error" sx={{ mb: 2 }}>{capabilitiesData.error}</Alert>
      )}

      {capabilitiesData && !capabilitiesData.error && (
        <>
          {/* Overall Banner */}
          <Alert severity={capabilitiesData.all_pass ? 'success' : 'warning'} sx={{ mb: 2 }} icon={capabilitiesData.all_pass ? <CheckCircleIcon /> : <WarningIcon />}>
            <strong>{capabilitiesData.all_pass ? 'ALL CAPABILITIES VERIFIED' : 'SOME CAPABILITIES FAILED'}</strong>
            {' — '}{capabilitiesData.capabilities_passed}/{capabilitiesData.total_capabilities} capabilities passed,
            {' '}{capabilitiesData.passed_checks}/{capabilitiesData.total_checks} checks passed
          </Alert>

          {/* Summary Cards */}
          <Grid container spacing={2} sx={{ mb: 3 }}>
            {[
              { label: 'Total Capabilities', value: capabilitiesData.total_capabilities, color: '#1976d2' },
              { label: 'Passed', value: capabilitiesData.capabilities_passed, color: '#2e7d32' },
              { label: 'Failed', value: capabilitiesData.capabilities_failed, color: capabilitiesData.capabilities_failed > 0 ? '#d32f2f' : '#2e7d32' },
              { label: 'Total Checks', value: capabilitiesData.total_checks, color: '#1976d2' },
              { label: 'Pass Rate', value: `${Math.round((capabilitiesData.passed_checks / capabilitiesData.total_checks) * 100)}%`, color: '#7b1fa2' },
              { label: 'Rules Active', value: `${capabilitiesData.rules_active}/${Array.isArray(capabilitiesData.rules_registry) ? capabilitiesData.rules_registry.length : capabilitiesData.rules_registry}`, color: '#0288d1' },
            ].map((c, i) => (
              <Grid item xs={6} sm={4} md={2} key={i}>
                <Paper sx={{ p: 2, textAlign: 'center', borderTop: `3px solid ${c.color}` }}>
                  <Typography variant="h5" fontWeight={700} color={c.color}>{c.value}</Typography>
                  <Typography variant="caption" color="text.secondary">{c.label}</Typography>
                </Paper>
              </Grid>
            ))}
          </Grid>

          {/* AML Rules Registry */}
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="subtitle1" fontWeight={600} gutterBottom>AML Rules Registry</Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Rule ID</TableCell>
                    <TableCell>Name</TableCell>
                    <TableCell>Category</TableCell>
                    <TableCell>Severity</TableCell>
                    <TableCell align="center">Status</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {(capabilitiesData.results?.[0]?.rules_registry_detail || []).length === 0 &&
                    capabilitiesData.rules_active > 0 && (
                    <TableRow><TableCell colSpan={5} align="center"><Typography variant="body2" color="text.secondary">Registry details included in capability results below.</Typography></TableCell></TableRow>
                  )}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* Per-Capability Accordions */}
          {capabilitiesData.results.map((cap, idx) => (
            <Accordion key={cap.id} defaultExpanded={cap.status?.toUpperCase() !== 'PASS'} sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" gap={1} width="100%">
                  <Chip label={cap.status} size="small" color={cap.status?.toUpperCase() === 'PASS' ? 'success' : 'error'} />
                  <Typography fontWeight={600}>{cap.capability}</Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto', mr: 2 }}>
                    {cap.passed}/{cap.total_checks} checks — {cap.pass_rate} — {cap.verification_latency_ms}ms
                  </Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="body2" color="text.secondary" mb={2}>{cap.description}</Typography>

                {/* Checks */}
                <Typography variant="subtitle2" gutterBottom>Checks</Typography>
                <Box sx={{ mb: 2 }}>
                  {cap.checks.map((ck, ci) => (
                    <Box key={ci} display="flex" alignItems="center" gap={1} sx={{ py: 0.5 }}>
                      {ck.status?.toUpperCase() === 'PASS' ? <CheckCircleIcon fontSize="small" color="success" /> : <CancelIcon fontSize="small" color="error" />}
                      <Typography variant="body2">{ck.check}</Typography>
                    </Box>
                  ))}
                </Box>

                {/* Scenarios */}
                {cap.scenarios && cap.scenarios.length > 0 && (
                  <>
                    <Typography variant="subtitle2" gutterBottom>Detection Scenarios</Typography>
                    <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Scenario</TableCell>
                            <TableCell>Rule</TableCell>
                            <TableCell>Description</TableCell>
                            <TableCell align="center">Status</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {cap.scenarios.map((sc, si) => (
                            <TableRow key={si}>
                              <TableCell><Typography variant="body2" fontWeight={600}>{sc.scenario}</Typography></TableCell>
                              <TableCell><Chip label={sc.rule} size="small" variant="outlined" /></TableCell>
                              <TableCell><Typography variant="body2">{sc.description}</Typography></TableCell>
                              <TableCell align="center"><Chip label={sc.status} size="small" color={sc.status?.toUpperCase() === 'PASS' ? 'success' : 'error'} /></TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                )}

                {/* Thresholds */}
                {cap.thresholds && cap.thresholds.length > 0 && (
                  <>
                    <Typography variant="subtitle2" gutterBottom>Threshold Rules</Typography>
                    <TableContainer component={Paper} variant="outlined" sx={{ mb: 2 }}>
                      <Table size="small">
                        <TableHead>
                          <TableRow>
                            <TableCell>Threshold</TableCell>
                            <TableCell>Value</TableCell>
                            <TableCell>Rule</TableCell>
                            <TableCell>Type</TableCell>
                            <TableCell align="center">Status</TableCell>
                          </TableRow>
                        </TableHead>
                        <TableBody>
                          {cap.thresholds.map((th, ti) => (
                            <TableRow key={ti}>
                              <TableCell><Typography variant="body2" fontWeight={600}>{th.name}</Typography></TableCell>
                              <TableCell><Typography variant="body2" fontFamily="monospace">{th.value}</Typography></TableCell>
                              <TableCell><Chip label={th.rule} size="small" variant="outlined" /></TableCell>
                              <TableCell><Chip label={th.type} size="small" color="info" variant="outlined" /></TableCell>
                              <TableCell align="center"><Chip label={th.status} size="small" color={th.status?.toUpperCase() === 'PASS' ? 'success' : 'error'} /></TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    </TableContainer>
                  </>
                )}

                {/* Throughput */}
                {cap.throughput && (
                  <Box display="flex" gap={2} mt={1}>
                    <Chip icon={<SpeedIcon />} label={`Capacity: ${cap.throughput.capacity}`} variant="outlined" />
                    <Chip icon={<TimerIcon />} label={`P95 Latency: ${cap.throughput.latency_p95}`} variant="outlined" />
                  </Box>
                )}

                {/* Data Sources */}
                {cap.data_sources && cap.data_sources.length > 0 && (
                  <Box mt={1}>
                    <Typography variant="subtitle2" gutterBottom>Data Sources</Typography>
                    <Box display="flex" gap={1} flexWrap="wrap">
                      {cap.data_sources.map((ds, di) => (
                        <Chip key={di} label={ds} size="small" variant="outlined" icon={<StorageIcon />} />
                      ))}
                    </Box>
                  </Box>
                )}
              </AccordionDetails>
            </Accordion>
          ))}
        </>
      )}
    </>
  );
}

// ═══════════════════ CDD/EDD Tab Component ═══════════════════
function CDDTab({ cddData, cddLoading, setCddData, setCddLoading }) {
  const [pepName, setPepName] = useState('');
  const [pepResult, setPepResult] = useState(null);
  const [pepLoading, setPepLoading] = useState(false);
  const [mediaName, setMediaName] = useState('');
  const [mediaResult, setMediaResult] = useState(null);
  const [mediaLoading, setMediaLoading] = useState(false);

  const loadCddData = async () => {
    setCddLoading(true);
    try {
      const [profilesRes, kycRes, eddRes] = await Promise.all([
        getCustomerProfiles(),
        checkOverdueReviews(),
        getEddWorkflows(),
      ]);
      setCddData({
        profiles: profilesRes.data,
        kycRefresh: kycRes.data,
        eddWorkflows: eddRes.data,
      });
    } catch (err) {
      console.error('Failed to load CDD data', err);
    } finally {
      setCddLoading(false);
    }
  };

  useEffect(() => { if (!cddData) loadCddData(); }, []);

  const handlePepScreen = async () => {
    if (!pepName.trim()) return;
    setPepLoading(true);
    try {
      const res = await screenPEP(pepName);
      setPepResult(res.data);
    } catch (err) { console.error(err); } finally { setPepLoading(false); }
  };

  const handleMediaScreen = async () => {
    if (!mediaName.trim()) return;
    setMediaLoading(true);
    try {
      const res = await screenAdverseMedia(mediaName);
      setMediaResult(res.data);
    } catch (err) { console.error(err); } finally { setMediaLoading(false); }
  };

  if (cddLoading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>;
  if (!cddData) return <Alert severity="info">Click Refresh to load CDD/EDD data.</Alert>;

  const { profiles, kycRefresh, eddWorkflows } = cddData;
  const riskColors = { low: 'success', medium: 'warning', high: 'error', critical: 'error' };
  const cddLabels = {
    simplified_due_diligence: 'Simplified DD',
    standard_due_diligence: 'Standard DD',
    enhanced_due_diligence: 'Enhanced DD',
  };

  return (
    <Box>
      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <Card><CardContent>
            <Typography variant="caption" color="text.secondary">Total Profiles</Typography>
            <Typography variant="h4" fontWeight={700}>{profiles?.total || 0}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderLeft: '4px solid #f44336' }}><CardContent>
            <Typography variant="caption" color="text.secondary">Overdue KYC Reviews</Typography>
            <Typography variant="h4" fontWeight={700} color="error">{kycRefresh?.overdue_count || 0}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderLeft: '4px solid #ff9800' }}><CardContent>
            <Typography variant="caption" color="text.secondary">Upcoming 30d Reviews</Typography>
            <Typography variant="h4" fontWeight={700} color="warning.main">{kycRefresh?.upcoming_30d_count || 0}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={3}>
          <Card sx={{ borderLeft: '4px solid #2196f3' }}><CardContent>
            <Typography variant="caption" color="text.secondary">Active EDD Workflows</Typography>
            <Typography variant="h4" fontWeight={700} color="primary">{eddWorkflows?.total || 0}</Typography>
          </CardContent></Card>
        </Grid>
      </Grid>

      {/* Customer Risk Profiles */}
      <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>Customer Risk Profiles</Typography>
      <TableContainer component={Paper} sx={{ mb: 3 }}>
        <Table size="small">
          <TableHead>
            <TableRow sx={{ backgroundColor: '#f5f5f5' }}>
              <TableCell><strong>Customer ID</strong></TableCell>
              <TableCell><strong>Name</strong></TableCell>
              <TableCell align="center"><strong>Risk Level</strong></TableCell>
              <TableCell align="center"><strong>Score</strong></TableCell>
              <TableCell align="center"><strong>CDD Level</strong></TableCell>
              <TableCell align="center"><strong>Review Freq.</strong></TableCell>
              <TableCell align="center"><strong>Next Review</strong></TableCell>
              <TableCell align="center"><strong>Status</strong></TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {(profiles?.profiles || []).map((p, i) => (
              <TableRow key={i} sx={{ '&:hover': { backgroundColor: '#fafafa' } }}>
                <TableCell><Typography variant="body2" fontFamily="monospace">{p.customer_id}</Typography></TableCell>
                <TableCell>{p.customer_name}</TableCell>
                <TableCell align="center">
                  <Chip label={p.risk_level} size="small" color={riskColors[p.risk_level] || 'default'} />
                </TableCell>
                <TableCell align="center">
                  <Typography variant="body2" fontWeight={600}>{(p.composite_score * 100).toFixed(0)}%</Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip label={cddLabels[p.cdd_level] || p.cdd_level} size="small" variant="outlined"
                    color={p.cdd_level === 'enhanced_due_diligence' ? 'error' : 'default'} />
                </TableCell>
                <TableCell align="center">{p.review_frequency}</TableCell>
                <TableCell align="center">
                  <Typography variant="body2" fontSize="0.8rem">
                    {p.next_review_date ? new Date(p.next_review_date).toLocaleDateString() : '—'}
                  </Typography>
                </TableCell>
                <TableCell align="center">
                  <Chip label={p.review_status} size="small"
                    color={p.review_status === 'completed' ? 'success' : p.review_status === 'overdue' ? 'error' : 'warning'} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Overdue KYC Reviews Alert */}
      {kycRefresh?.overdue_count > 0 && (
        <Alert severity="error" sx={{ mb: 3 }}>
          <strong>{kycRefresh.overdue_count} customer(s) have overdue KYC reviews.</strong> Immediate action required.
          {kycRefresh.overdue.map((o, i) => (
            <Box key={i} ml={2} mt={0.5}>
              • {o.customer_id} — Risk: {o.risk_level}, CDD: {o.cdd_level}, Due: {new Date(o.next_review_date).toLocaleDateString()}
            </Box>
          ))}
        </Alert>
      )}

      {/* EDD Workflows */}
      <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>EDD Workflows</Typography>
      {(eddWorkflows?.workflows || []).map((wf, wi) => (
        <Accordion key={wi} sx={{ mb: 1 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" gap={2} width="100%">
              <Chip label={wf.status} size="small" color={wf.status === 'completed' ? 'success' : wf.status === 'rejected' ? 'error' : 'warning'} />
              <Typography fontWeight={600}>{wf.customer_name}</Typography>
              <Chip label={wf.risk_level} size="small" color={riskColors[wf.risk_level] || 'default'} variant="outlined" />
              <Typography variant="body2" color="text.secondary" sx={{ ml: 'auto', mr: 2 }}>
                SLA: {new Date(wf.sla_deadline).toLocaleDateString()}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <Typography variant="subtitle2" sx={{ mb: 1 }}>EDD Checklist ({wf.checklist.filter(c => c.status === 'completed').length}/{wf.checklist.length} completed)</Typography>
            <LinearProgress variant="determinate"
              value={(wf.checklist.filter(c => c.status === 'completed').length / wf.checklist.length) * 100}
              sx={{ mb: 2, height: 8, borderRadius: 4 }} />
            <Table size="small">
              <TableBody>
                {wf.checklist.map((item, ci) => (
                  <TableRow key={ci}>
                    <TableCell sx={{ width: 40 }}>
                      {item.status === 'completed' ? <CheckCircleIcon color="success" fontSize="small" /> :
                       item.status === 'not_required' ? <CancelIcon color="disabled" fontSize="small" /> :
                       <ScheduleIcon color="warning" fontSize="small" />}
                    </TableCell>
                    <TableCell>{item.label}</TableCell>
                    <TableCell align="center">
                      {item.required ? <Chip label="Required" size="small" color="error" variant="outlined" /> :
                       <Chip label="Optional" size="small" variant="outlined" />}
                    </TableCell>
                    <TableCell align="center">
                      <Chip label={item.status} size="small"
                        color={item.status === 'completed' ? 'success' : item.status === 'not_required' ? 'default' : 'warning'} />
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </AccordionDetails>
        </Accordion>
      ))}

      <Divider sx={{ my: 3 }} />

      {/* PEP Screening */}
      <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>PEP Screening (with RCA Detection)</Typography>
      <Box display="flex" gap={1} mb={2}>
        <TextField size="small" label="Name to screen" value={pepName} onChange={e => setPepName(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handlePepScreen()} sx={{ minWidth: 300 }} />
        <Button variant="contained" onClick={handlePepScreen} disabled={pepLoading} startIcon={pepLoading ? <CircularProgress size={16} /> : <PersonSearchIcon />}>
          Screen PEP
        </Button>
      </Box>
      {pepResult && (
        <Box mb={3}>
          {pepResult.is_pep && (
            <Alert severity="error" sx={{ mb: 1 }}>
              <strong>PEP MATCH:</strong> {pepResult.pep_matches.map(m => `${m.matched_name} (${m.position}, ${m.country}) — Score: ${(m.match_score * 100).toFixed(0)}%`).join('; ')}
            </Alert>
          )}
          {pepResult.is_rca && (
            <Alert severity="warning" sx={{ mb: 1 }}>
              <strong>RCA MATCH (Relative/Close Associate):</strong> {pepResult.rca_matches.map(m => `${m.rca_name} — ${m.relationship} of ${m.pep_name} (${m.pep_position})`).join('; ')}
            </Alert>
          )}
          {!pepResult.is_pep && !pepResult.is_rca && (
            <Alert severity="success" sx={{ mb: 1 }}>No PEP or RCA matches found for "{pepResult.screened_name}".</Alert>
          )}
          <Typography variant="caption" color="text.secondary">
            Engine: {pepResult.engine_stats?.total_pep_entries} PEP entries, {pepResult.engine_stats?.total_rca_entries} RCA entries
          </Typography>
        </Box>
      )}

      {/* Adverse Media Screening */}
      <Typography variant="h6" fontWeight={700} sx={{ mb: 1 }}>Adverse Media Screening</Typography>
      <Box display="flex" gap={1} mb={2}>
        <TextField size="small" label="Name to screen" value={mediaName} onChange={e => setMediaName(e.target.value)}
          onKeyDown={e => e.key === 'Enter' && handleMediaScreen()} sx={{ minWidth: 300 }} />
        <Button variant="contained" color="secondary" onClick={handleMediaScreen} disabled={mediaLoading}
          startIcon={mediaLoading ? <CircularProgress size={16} /> : <PersonSearchIcon />}>
          Screen Media
        </Button>
      </Box>
      {mediaResult && (
        <Box mb={3}>
          {mediaResult.has_adverse_media ? (
            <Alert severity="error" sx={{ mb: 1 }}>
              <strong>ADVERSE MEDIA FOUND — Severity: {mediaResult.highest_severity?.toUpperCase()}</strong>
              {mediaResult.matches.map((m, i) => (
                <Box key={i} ml={2} mt={0.5}>
                  • [{m.severity.toUpperCase()}] {m.headline} — Source: {m.source} ({m.published_date})
                </Box>
              ))}
            </Alert>
          ) : (
            <Alert severity="success">No adverse media found for "{mediaResult.screened_name}".</Alert>
          )}
          <Typography variant="caption" color="text.secondary">
            Engine: {mediaResult.engine_stats?.total_entries} media entries across {mediaResult.engine_stats?.categories?.length} categories
          </Typography>
        </Box>
      )}

      <Box mt={2}>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadCddData} disabled={cddLoading}>
          Refresh CDD/EDD Data
        </Button>
      </Box>
    </Box>
  );
}

/* ========================= WLF TAB ========================= */
function WLFTab({ wlfData, wlfLoading, setWlfData, setWlfLoading }) {
  const [paymentForm, setPaymentForm] = useState({
    beneficiary_name: '', originator_name: '', amount: '', currency: 'USD', payment_type: 'wire',
  });
  const [paymentResult, setPaymentResult] = useState(null);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [nameInput, setNameInput] = useState('');
  const [nameResult, setNameResult] = useState(null);
  const [nameLoading, setNameLoading] = useState(false);

  const loadWlfData = async () => {
    setWlfLoading(true);
    try {
      const [alertsRes, groupsRes, statsRes, batchRes] = await Promise.all([
        getWlfAlerts(),
        getWlfAlertGroups(),
        getWlfAlertStats(),
        wlfScreenBatch({}),
      ]);
      setWlfData({
        alerts: alertsRes.data,
        groups: groupsRes.data,
        stats: statsRes.data,
        batch: batchRes.data,
      });
    } catch (err) {
      console.error('Failed to load WLF data', err);
    } finally {
      setWlfLoading(false);
    }
  };

  useEffect(() => { if (!wlfData) loadWlfData(); }, []);

  const handlePaymentScreen = async () => {
    if (!paymentForm.beneficiary_name.trim()) return;
    setPaymentLoading(true);
    try {
      const res = await wlfScreenPayment({
        ...paymentForm,
        amount: parseFloat(paymentForm.amount) || 0,
      });
      setPaymentResult(res.data);
    } catch (err) { console.error(err); } finally { setPaymentLoading(false); }
  };

  const handleNameScreen = async () => {
    if (!nameInput.trim()) return;
    setNameLoading(true);
    try {
      const res = await wlfScreenName(nameInput);
      setNameResult(res.data);
    } catch (err) { console.error(err); } finally { setNameLoading(false); }
  };

  if (wlfLoading) return <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>;
  if (!wlfData) return <Alert severity="info">Click Refresh to load WLF data.</Alert>;

  const { alerts, groups, stats, batch } = wlfData;
  const priorityColors = { critical: '#d32f2f', high: '#f57c00', medium: '#fbc02d', low: '#4caf50' };
  const decisionColors = { BLOCK: 'error', HOLD: 'warning', RELEASE: 'success' };
  const dispositionColors = {
    likely_true_positive: 'error', review_required: 'warning',
    likely_false_positive: 'info', auto_dismiss: 'default',
  };

  return (
    <Box>
      {/* Summary Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={2.4}>
          <Card><CardContent>
            <Typography variant="caption" color="text.secondary">Total Alerts</Typography>
            <Typography variant="h4" fontWeight={700}>{stats?.total_alerts || 0}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={2.4}>
          <Card sx={{ borderLeft: '4px solid #d32f2f' }}><CardContent>
            <Typography variant="caption" color="text.secondary">Critical</Typography>
            <Typography variant="h4" fontWeight={700} color="error">{stats?.by_priority?.critical || 0}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={2.4}>
          <Card sx={{ borderLeft: '4px solid #f57c00' }}><CardContent>
            <Typography variant="caption" color="text.secondary">High</Typography>
            <Typography variant="h4" fontWeight={700} sx={{ color: '#f57c00' }}>{stats?.by_priority?.high || 0}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={2.4}>
          <Card sx={{ borderLeft: '4px solid #4caf50' }}><CardContent>
            <Typography variant="caption" color="text.secondary">Matching Methods</Typography>
            <Typography variant="h4" fontWeight={700} color="success.main">{stats?.matching_methods?.length || 0}</Typography>
          </CardContent></Card>
        </Grid>
        <Grid item xs={12} md={2.4}>
          <Card sx={{ borderLeft: '4px solid #1976d2' }}><CardContent>
            <Typography variant="caption" color="text.secondary">ML Features</Typography>
            <Typography variant="h4" fontWeight={700} color="primary">{stats?.ml_model?.features || 0}</Typography>
          </CardContent></Card>
        </Grid>
      </Grid>

      {/* Payment Screening */}
      <Accordion defaultExpanded sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" fontWeight={600}>Real-Time Payment Screening</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={12} md={3}>
              <TextField fullWidth size="small" label="Beneficiary Name" value={paymentForm.beneficiary_name}
                onChange={(e) => setPaymentForm(p => ({ ...p, beneficiary_name: e.target.value }))} />
            </Grid>
            <Grid item xs={12} md={3}>
              <TextField fullWidth size="small" label="Originator Name" value={paymentForm.originator_name}
                onChange={(e) => setPaymentForm(p => ({ ...p, originator_name: e.target.value }))} />
            </Grid>
            <Grid item xs={12} md={1.5}>
              <TextField fullWidth size="small" label="Amount" type="number" value={paymentForm.amount}
                onChange={(e) => setPaymentForm(p => ({ ...p, amount: e.target.value }))} />
            </Grid>
            <Grid item xs={12} md={1.5}>
              <TextField fullWidth size="small" label="Currency" select value={paymentForm.currency}
                onChange={(e) => setPaymentForm(p => ({ ...p, currency: e.target.value }))}>
                {['USD', 'EUR', 'GBP', 'CHF'].map(c => <MenuItem key={c} value={c}>{c}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12} md={1.5}>
              <TextField fullWidth size="small" label="Type" select value={paymentForm.payment_type}
                onChange={(e) => setPaymentForm(p => ({ ...p, payment_type: e.target.value }))}>
                {['wire', 'ach', 'swift', 'sepa'].map(t => <MenuItem key={t} value={t}>{t.toUpperCase()}</MenuItem>)}
              </TextField>
            </Grid>
            <Grid item xs={12} md={1.5}>
              <Button fullWidth variant="contained" onClick={handlePaymentScreen} disabled={paymentLoading}
                sx={{ height: '40px' }}>
                {paymentLoading ? <CircularProgress size={20} /> : 'Screen'}
              </Button>
            </Grid>
          </Grid>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
            Try: "Acme Trading" or "Ivan Petrov" as beneficiary for a BLOCK result
          </Typography>
          {paymentResult && (
            <Card variant="outlined" sx={{ mt: 2 }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Chip label={paymentResult.decision} color={decisionColors[paymentResult.decision] || 'default'} size="medium" sx={{ fontWeight: 700, fontSize: 16 }} />
                  <Typography variant="body2" color="text.secondary">{paymentResult.reason}</Typography>
                  <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto' }}>
                    Latency: {paymentResult.latency_ms}ms
                  </Typography>
                </Box>
                {paymentResult.matches?.length > 0 && (
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead><TableRow sx={{ bgcolor: '#fafafa' }}>
                        <TableCell>Direction</TableCell><TableCell>List</TableCell><TableCell>Entity</TableCell>
                        <TableCell>Score</TableCell><TableCell>Type</TableCell><TableCell>Country</TableCell>
                        <TableCell>TP Prob</TableCell><TableCell>ML Disposition</TableCell>
                      </TableRow></TableHead>
                      <TableBody>
                        {paymentResult.matches.map((m, i) => (
                          <TableRow key={i}>
                            <TableCell><Chip label={m.direction} size="small" /></TableCell>
                            <TableCell><Chip label={m.list_name} size="small" color="primary" variant="outlined" /></TableCell>
                            <TableCell fontWeight={600}>{m.entity_name}</TableCell>
                            <TableCell>{(m.match_score * 100).toFixed(0)}%</TableCell>
                            <TableCell><Chip label={m.match_type} size="small" variant="outlined" /></TableCell>
                            <TableCell>{m.country}</TableCell>
                            <TableCell>{(m.tp_probability * 100).toFixed(0)}%</TableCell>
                            <TableCell><Chip label={m.ml_disposition?.replace(/_/g, ' ')} size="small"
                              color={dispositionColors[m.ml_disposition] || 'default'} /></TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
                {paymentResult.alert_id && (
                  <Alert severity="warning" sx={{ mt: 2 }}>
                    Alert <strong>{paymentResult.alert_id}</strong> created &mdash; Priority: <strong>{paymentResult.alert_priority}</strong>
                  </Alert>
                )}
              </CardContent>
            </Card>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Name Screening */}
      <Accordion defaultExpanded sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" fontWeight={600}>Name Screening (Multi-Method)</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box display="flex" gap={2} mb={2}>
            <TextField fullWidth size="small" label="Name to screen" value={nameInput}
              onChange={(e) => setNameInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleNameScreen()} />
            <Button variant="contained" onClick={handleNameScreen} disabled={nameLoading} sx={{ minWidth: { xs: 80, sm: 120 } }}>
              {nameLoading ? <CircularProgress size={20} /> : 'Screen'}
            </Button>
          </Box>
          <Typography variant="caption" color="text.secondary" sx={{ mb: 1, display: 'block' }}>
            Try: "Jon Doe" (phonetic), "Mohammed Ali" (romanisation), "Ivan Petroff" (alias)
          </Typography>
          {nameResult && (
            <Card variant="outlined" sx={{ mt: 2 }}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={2} mb={2}>
                  <Typography variant="subtitle1" fontWeight={600}>
                    Screened: "{nameResult.name_screened}"
                  </Typography>
                  <Chip label={nameResult.is_match ? `${nameResult.total_matches} match(es)` : 'No Match'}
                    color={nameResult.is_match ? 'error' : 'success'} size="small" />
                </Box>
                <Box display="flex" gap={0.5} flexWrap="wrap" mb={2}>
                  {nameResult.matching_methods_used?.map(m => (
                    <Chip key={m} label={m} size="small" variant="outlined" color="primary" />
                  ))}
                </Box>
                {nameResult.matches?.length > 0 && (
                  <TableContainer component={Paper} variant="outlined">
                    <Table size="small">
                      <TableHead><TableRow sx={{ bgcolor: '#fafafa' }}>
                        <TableCell>List</TableCell><TableCell>Entity</TableCell><TableCell>Score</TableCell>
                        <TableCell>Match Type</TableCell><TableCell>Country</TableCell>
                        <TableCell>TP Prob</TableCell><TableCell>ML Disposition</TableCell>
                      </TableRow></TableHead>
                      <TableBody>
                        {nameResult.matches.map((m, i) => (
                          <TableRow key={i}>
                            <TableCell><Chip label={m.list_name} size="small" color="primary" variant="outlined" /></TableCell>
                            <TableCell fontWeight={600}>{m.entity_name}</TableCell>
                            <TableCell>{(m.match_score * 100).toFixed(0)}%</TableCell>
                            <TableCell><Chip label={m.match_type} size="small" variant="outlined"
                              sx={{ bgcolor: m.match_type.includes('phonetic') ? '#e3f2fd' : m.match_type === 'romanisation' ? '#f3e5f5' : m.match_type === 'exact' ? '#e8f5e9' : 'transparent' }} /></TableCell>
                            <TableCell>{m.country}</TableCell>
                            <TableCell>{(m.tp_probability * 100).toFixed(0)}%</TableCell>
                            <TableCell><Chip label={m.ml_disposition?.replace(/_/g, ' ')} size="small"
                              color={dispositionColors[m.ml_disposition] || 'default'} /></TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                )}
              </CardContent>
            </Card>
          )}
        </AccordionDetails>
      </Accordion>

      {/* Batch Screening Results */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h6" fontWeight={600}>Batch Screening Results</Typography>
            <Chip label={`${batch?.total_customers || 0} customers`} size="small" color="primary" />
            <Chip label={`${batch?.total_auto_dismissed || 0} auto-dismissed`} size="small" color="success" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2} sx={{ mb: 2 }}>
            <Grid item xs={6} md={3}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="caption" color="text.secondary">Screened</Typography>
                <Typography variant="h5" fontWeight={700}>{batch?.total_customers || 0}</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="caption" color="text.secondary">With Matches</Typography>
                <Typography variant="h5" fontWeight={700} color="error">{batch?.customers_with_matches || 0}</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="caption" color="text.secondary">Actionable</Typography>
                <Typography variant="h5" fontWeight={700} color="warning.main">{batch?.total_actionable_matches || 0}</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={6} md={3}>
              <Card variant="outlined"><CardContent sx={{ textAlign: 'center', py: 1 }}>
                <Typography variant="caption" color="text.secondary">Auto-Dismissed (ML)</Typography>
                <Typography variant="h5" fontWeight={700} color="success.main">{batch?.total_auto_dismissed || 0}</Typography>
              </CardContent></Card>
            </Grid>
          </Grid>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead><TableRow sx={{ bgcolor: '#fafafa' }}>
                <TableCell>Customer ID</TableCell><TableCell>Matched Entity</TableCell><TableCell>List</TableCell>
                <TableCell>Score</TableCell><TableCell>Type</TableCell><TableCell>TP Prob</TableCell>
                <TableCell>ML Disposition</TableCell><TableCell>Auto-Dismissed</TableCell>
              </TableRow></TableHead>
              <TableBody>
                {batch?.results?.map((r, i) => (
                  r.matches?.length > 0 ? r.matches.map((m, j) => (
                    <TableRow key={`${i}-${j}`}>
                      {j === 0 && <TableCell rowSpan={r.matches.length}>{r.customer_id}</TableCell>}
                      <TableCell>{m.matched_name || m.entity_name}</TableCell>
                      <TableCell><Chip label={m.list_name} size="small" color="primary" variant="outlined" /></TableCell>
                      <TableCell>{(m.match_score * 100).toFixed(0)}%</TableCell>
                      <TableCell><Chip label={m.match_type} size="small" variant="outlined" /></TableCell>
                      <TableCell>{(m.tp_probability * 100).toFixed(0)}%</TableCell>
                      <TableCell><Chip label={m.ml_disposition?.replace(/_/g, ' ')} size="small"
                        color={dispositionColors[m.ml_disposition] || 'default'} /></TableCell>
                      {j === 0 && <TableCell rowSpan={r.matches.length}>
                        {r.auto_dismissed > 0 ? <Chip label={`${r.auto_dismissed} dismissed`} size="small" color="success" /> : '—'}
                      </TableCell>}
                    </TableRow>
                  )) : (
                    <TableRow key={i}>
                      <TableCell>{r.customer_id}</TableCell>
                      <TableCell colSpan={6}><Typography variant="caption" color="text.secondary">No matches</Typography></TableCell>
                      <TableCell>—</TableCell>
                    </TableRow>
                  )
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Box display="flex" gap={0.5} flexWrap="wrap" mt={2}>
            <Typography variant="caption" color="text.secondary" sx={{ mr: 1 }}>Lists screened:</Typography>
            {batch?.lists_screened?.map(l => <Chip key={l} label={l} size="small" variant="outlined" />)}
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Alert List */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h6" fontWeight={600}>WLF Alerts</Typography>
            <Chip label={`${alerts?.total || 0} alerts`} size="small" color="error" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <TableContainer component={Paper} variant="outlined">
            <Table size="small">
              <TableHead><TableRow sx={{ bgcolor: '#fafafa' }}>
                <TableCell>Alert ID</TableCell><TableCell>Priority</TableCell><TableCell>Source</TableCell>
                <TableCell>Entity</TableCell><TableCell>Top Match</TableCell><TableCell>Score</TableCell>
                <TableCell>Type</TableCell><TableCell>ML Disposition</TableCell><TableCell>Status</TableCell>
              </TableRow></TableHead>
              <TableBody>
                {alerts?.alerts?.map((a) => (
                  <TableRow key={a.alert_id} sx={{ borderLeft: `4px solid ${priorityColors[a.priority] || '#ccc'}` }}>
                    <TableCell sx={{ fontFamily: 'monospace', fontWeight: 600 }}>{a.alert_id}</TableCell>
                    <TableCell><Chip label={a.priority} size="small"
                      sx={{ bgcolor: priorityColors[a.priority], color: a.priority === 'medium' ? '#000' : '#fff', fontWeight: 700 }} /></TableCell>
                    <TableCell><Chip label={a.source?.replace('_', ' ')} size="small" variant="outlined" /></TableCell>
                    <TableCell fontWeight={600}>{a.screened_entity}</TableCell>
                    <TableCell>
                      <Typography variant="body2">{a.top_match?.entity_name}</Typography>
                      <Typography variant="caption" color="text.secondary">{a.top_match?.list_name}</Typography>
                    </TableCell>
                    <TableCell>{(a.top_match?.match_score * 100).toFixed(0)}%</TableCell>
                    <TableCell><Chip label={a.top_match?.match_type} size="small" variant="outlined" /></TableCell>
                    <TableCell><Chip label={a.top_match?.ml_disposition?.replace(/_/g, ' ')} size="small"
                      color={dispositionColors[a.top_match?.ml_disposition] || 'default'} /></TableCell>
                    <TableCell><Chip label={a.status} size="small" color={a.status === 'open' ? 'warning' : 'success'} /></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </AccordionDetails>
      </Accordion>

      {/* Alert Groups */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Box display="flex" alignItems="center" gap={2}>
            <Typography variant="h6" fontWeight={600}>Alert Groups</Typography>
            <Chip label={`${groups?.total || 0} groups`} size="small" />
          </Box>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            {groups?.groups?.map((g) => (
              <Grid item xs={12} md={6} key={g.group_key}>
                <Card variant="outlined" sx={{ borderLeft: `4px solid ${priorityColors[g.highest_priority] || '#ccc'}` }}>
                  <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box>
                        <Typography variant="subtitle2" fontWeight={700}>{g.entity_name}</Typography>
                        <Chip label={g.list_name} size="small" color="primary" variant="outlined" sx={{ mt: 0.5 }} />
                      </Box>
                      <Box textAlign="right">
                        <Chip label={g.highest_priority} size="small"
                          sx={{ bgcolor: priorityColors[g.highest_priority], color: g.highest_priority === 'medium' ? '#000' : '#fff', fontWeight: 700, mb: 0.5 }} />
                        <Typography variant="caption" display="block" color="text.secondary">
                          {g.total_alerts} alert(s) &bull; Score: {(g.highest_score * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        </AccordionDetails>
      </Accordion>

      {/* ML Model & Matching Methods */}
      <Accordion sx={{ mb: 2 }}>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="h6" fontWeight={600}>ML Model &amp; Matching Methods</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" fontWeight={700} gutterBottom>Matching Methods</Typography>
              <Box display="flex" flexWrap="wrap" gap={1}>
                {stats?.matching_methods?.map(m => (
                  <Chip key={m} label={m} color="primary" variant="outlined"
                    icon={m.includes('phonetic') ? <SpeedIcon /> : m === 'exact' ? <CheckCircleIcon /> : undefined} />
                ))}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Typography variant="subtitle2" fontWeight={700} gutterBottom>ML False-Positive Reduction</Typography>
              <Box>
                <Typography variant="body2">Model: <strong>{stats?.ml_model?.type?.replace(/_/g, ' ')}</strong></Typography>
                <Typography variant="body2">Features: <strong>{stats?.ml_model?.features}</strong></Typography>
                <Typography variant="body2" sx={{ mt: 1 }}>Dispositions:</Typography>
                <Box display="flex" gap={1} flexWrap="wrap" mt={0.5}>
                  {stats?.ml_model?.dispositions?.map(d => (
                    <Chip key={d} label={d.replace(/_/g, ' ')} size="small"
                      color={dispositionColors[d] || 'default'} />
                  ))}
                </Box>
              </Box>
            </Grid>
          </Grid>
        </AccordionDetails>
      </Accordion>

      <Box display="flex" justifyContent="flex-end" mt={2}>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadWlfData} disabled={wlfLoading}>
          Refresh WLF Data
        </Button>
      </Box>
    </Box>
  );
}

/* ========================= EFM TAB (Enterprise Fraud Management) ========================= */
function EFMTab({ efmData, efmLoading, setEfmData, setEfmLoading }) {
  const [atoResult, setAtoResult] = useState(null);
  const [muleResult, setMuleResult] = useState(null);
  const [cardResult, setCardResult] = useState(null);
  const [deviceResult, setDeviceResult] = useState(null);
  const [biometricsResult, setBiometricsResult] = useState(null);
  const [paymentResult, setPaymentResult] = useState(null);
  const [crossChannelResult, setCrossChannelResult] = useState(null);
  const [runningEngine, setRunningEngine] = useState(null);

  const loadEfmInfo = async () => {
    setEfmLoading(true);
    try {
      const res = await getEfmInfo();
      setEfmData(res.data);
    } catch { setEfmData(null); }
    finally { setEfmLoading(false); }
  };

  useEffect(() => { if (!efmData) loadEfmInfo(); }, []);

  const runScenario = async (name, apiFn, setter, params = {}) => {
    setRunningEngine(name);
    try {
      const res = await apiFn(params);
      setter(res.data);
    } catch { setter(null); }
    finally { setRunningEngine(null); }
  };

  const riskColor = (level) => {
    if (!level) return 'default';
    if (level === 'critical') return 'error';
    if (level === 'high') return 'warning';
    if (level === 'medium') return 'info';
    return 'success';
  };

  const ScoreDisplay = ({ label, score, riskLevel, icon }) => (
    <Box display="flex" alignItems="center" gap={1} mb={1}>
      {icon}
      <Typography variant="body2" fontWeight={600} sx={{ minWidth: 160 }}>{label}:</Typography>
      <LinearProgress variant="determinate" value={(score || 0) * 100}
        sx={{ flex: 1, height: 10, borderRadius: 5,
          '& .MuiLinearProgress-bar': { backgroundColor: score >= 0.7 ? '#d32f2f' : score >= 0.4 ? '#ed6c02' : '#2e7d32' }
        }} />
      <Typography variant="body2" fontWeight={600} sx={{ minWidth: 50, textAlign: 'right' }}>
        {score != null ? (score * 100).toFixed(1) + '%' : '—'}
      </Typography>
      {riskLevel && <Chip size="small" label={riskLevel} color={riskColor(riskLevel)} />}
    </Box>
  );

  const ResultCard = ({ title, icon, result, onRun, engineName, children }) => (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {icon}
            <Typography variant="h6" fontWeight={700}>{title}</Typography>
          </Box>
          <Button variant="contained" size="small" onClick={onRun}
            disabled={runningEngine === engineName}
            startIcon={runningEngine === engineName ? <CircularProgress size={16} /> : <PlaylistAddCheckIcon />}>
            {result ? 'Re-run' : 'Simulate'}
          </Button>
        </Box>
        {result && children}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Engine Status Overview */}
      <Card variant="outlined" sx={{ mb: 3, bgcolor: 'grey.50' }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <ShieldIcon color="primary" />
            <Typography variant="h6" fontWeight={700}>EFM Engine Status</Typography>
            <Box flex={1} />
            <Button size="small" variant="outlined" onClick={loadEfmInfo} disabled={efmLoading}
              startIcon={efmLoading ? <CircularProgress size={16} /> : <RefreshIcon />}>Refresh</Button>
          </Box>
          {efmData ? (
            <Grid container spacing={1}>
              {efmData.engines?.map((eng, i) => (
                <Grid item xs={12} sm={6} md={4} key={i}>
                  <Box display="flex" alignItems="center" gap={1} p={1} bgcolor="white" borderRadius={1}>
                    <CheckCircleIcon color="success" fontSize="small" />
                    <Box>
                      <Typography variant="body2" fontWeight={600}>{eng.name}</Typography>
                      <Typography variant="caption" color="text.secondary">{eng.description}</Typography>
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          ) : efmLoading ? <CircularProgress size={24} /> : (
            <Alert severity="info">Click Refresh to load engine status</Alert>
          )}
          {efmData && (
            <Box display="flex" gap={2} mt={2}>
              <Chip label={`${efmData.total_engines} Engines Active`} color="success" size="small" icon={<CheckCircleIcon />} />
              <Chip label={`${efmData.payment_rails?.length} Payment Rails`} color="primary" size="small" icon={<PaymentIcon />} />
              <Chip label={`${efmData.mcc_risk_entries} High-Risk MCC Codes`} color="warning" size="small" icon={<CreditCardIcon />} />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* Scenario 1: Account Takeover */}
      <ResultCard title="Account Takeover Detection" icon={<LockIcon color="error" />}
        result={atoResult} engineName="ato"
        onRun={() => runScenario('ato', efmAtoSimulate, setAtoResult, {
          customer_id: 'CUST-ATO-DEMO', events: [
            { type: 'device_change', metadata: { device_id: 'DEV-NEW-999', vpn: true } },
            { type: 'failed_login', metadata: { attempts: 3 } },
            { type: 'failed_login', metadata: {} }, { type: 'failed_login', metadata: {} },
            { type: 'password_reset', metadata: { method: 'email' } },
            { type: 'high_value_transfer', metadata: { amount: 45000, destination: 'offshore' } },
          ]
        })}>
        {atoResult && (
          <Box>
            <ScoreDisplay label="ATO Score" score={atoResult.ato_score} riskLevel={atoResult.risk_level} icon={<LockIcon fontSize="small" />} />
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Signals Detected</Typography>
                {atoResult.signals && Object.entries(atoResult.signals).map(([k, v]) => (
                  <Chip key={k} size="small" label={k.replace(/_/g, ' ')} sx={{ mr: 0.5, mb: 0.5 }}
                    color={v ? 'error' : 'default'} variant={v ? 'filled' : 'outlined'} />
                ))}
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Triggered Patterns</Typography>
                {atoResult.triggered_patterns?.map((p, i) => (
                  <Chip key={i} size="small" label={p} color="error" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Grid>
            </Grid>
            {atoResult.is_ato && (
              <Alert severity="error" sx={{ mt: 2 }}>
                <strong>FULL ATO CHAIN DETECTED</strong> — New device login &rarr; Password reset &rarr; High-value transfer
              </Alert>
            )}
          </Box>
        )}
      </ResultCard>

      {/* Scenario 2: Mule Account Detection */}
      <ResultCard title="Mule Account Detection" icon={<AccountTreeIcon color="warning" />}
        result={muleResult} engineName="mule"
        onRun={() => runScenario('mule', efmMuleSimulate, setMuleResult, { customer_id: 'CUST-MULE-DEMO' })}>
        {muleResult && (
          <Box>
            <ScoreDisplay label="Mule Score" score={muleResult.mule_score} riskLevel={muleResult.risk_level} icon={<AccountTreeIcon fontSize="small" />} />
            <Grid container spacing={2} mt={1}>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Detected Patterns</Typography>
                {muleResult.patterns?.map((p, i) => (
                  <Box key={i} mb={1} p={1} bgcolor="grey.50" borderRadius={1}>
                    <Typography variant="body2" fontWeight={600}>{p.pattern.replace(/_/g, ' ')}</Typography>
                    <Typography variant="caption" color="text.secondary">{p.detail}</Typography>
                  </Box>
                ))}
              </Grid>
              <Grid item xs={12} md={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Transaction Stats</Typography>
                <Table size="small">
                  <TableBody>
                    {muleResult.stats && Object.entries(muleResult.stats).map(([k, v]) => (
                      <TableRow key={k}>
                        <TableCell sx={{ fontWeight: 600, textTransform: 'capitalize' }}>{k.replace(/_/g, ' ')}</TableCell>
                        <TableCell align="right">{typeof v === 'number' && v > 100 ? `$${v.toLocaleString()}` : v}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Grid>
            </Grid>
            {muleResult.is_mule && (
              <Alert severity="warning" sx={{ mt: 2 }}>
                <strong>MULE ACCOUNT DETECTED</strong> — Multiple P2P deposits from different senders followed by rapid cash withdrawal
              </Alert>
            )}
          </Box>
        )}
      </ResultCard>

      {/* Scenario 3: Card Fraud Detection */}
      <ResultCard title="Card Fraud Detection" icon={<CreditCardIcon color="primary" />}
        result={cardResult} engineName="card"
        onRun={() => runScenario('card', efmCardSimulate, setCardResult, {
          mcc: '7995', merchant_country: 'NG', amount: 8500, home_country: 'US'
        })}>
        {cardResult && (
          <Box>
            <ScoreDisplay label="Card Fraud Score" score={cardResult.card_fraud_score} riskLevel={cardResult.risk_level} icon={<CreditCardIcon fontSize="small" />} />
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Table size="small">
                  <TableBody>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>MCC</TableCell><TableCell>{cardResult.mcc} — {cardResult.mcc_description}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Merchant Country</TableCell><TableCell>{cardResult.merchant_country}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Home Country</TableCell><TableCell>{cardResult.home_country}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Amount</TableCell><TableCell>${cardResult.amount?.toLocaleString()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Foreign Transaction</TableCell><TableCell>{cardResult.is_foreign ? 'Yes' : 'No'}</TableCell></TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Risk Flags</Typography>
                {cardResult.flags?.map((f, i) => (
                  <Chip key={i} size="small" label={f.replace(/_/g, ' ')} color="error" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Grid>
            </Grid>
          </Box>
        )}
      </ResultCard>

      {/* Device Fingerprint */}
      <ResultCard title="Device Fingerprint Assessment" icon={<FingerprintIcon color="secondary" />}
        result={deviceResult} engineName="device"
        onRun={() => runScenario('device', efmDeviceSimulate, setDeviceResult, {
          is_known: false, device: { device_id: 'DEV-NEW-XYZ', vpn_flag: true, is_tor: false, is_emulator: false }
        })}>
        {deviceResult && (
          <Box>
            <ScoreDisplay label="Device Trust" score={deviceResult.trust_score} icon={<FingerprintIcon fontSize="small" />} />
            <Box display="flex" gap={1} flexWrap="wrap" mt={1}>
              <Chip size="small" label={deviceResult.is_known ? 'Known Device' : 'New Device'} color={deviceResult.is_known ? 'success' : 'error'} />
              <Chip size="small" label={`Age: ${deviceResult.device_age_days}d`} variant="outlined" />
              {deviceResult.risk_flags?.map((f, i) => (
                <Chip key={i} size="small" label={f.replace(/_/g, ' ')} color="warning" />
              ))}
            </Box>
          </Box>
        )}
      </ResultCard>

      {/* Behavioral Biometrics */}
      <ResultCard title="Behavioral Biometrics Analysis" icon={<DevicesIcon color="info" />}
        result={biometricsResult} engineName="biometrics"
        onRun={() => runScenario('biometrics', efmBiometricsSimulate, setBiometricsResult, { is_anomalous: true })}>
        {biometricsResult && (
          <Box>
            <ScoreDisplay label="Anomaly Score" score={biometricsResult.anomaly_score} icon={<DevicesIcon fontSize="small" />} />
            <Box display="flex" gap={1} mb={1}>
              <Chip size="small" label={`Verdict: ${biometricsResult.verdict}`}
                color={biometricsResult.verdict === 'anomalous' ? 'error' : 'success'} />
              <Chip size="small" label={`Confidence: ${(biometricsResult.confidence * 100).toFixed(0)}%`} variant="outlined" />
              <Chip size="small" label={`${biometricsResult.baseline_sessions} baseline sessions`} variant="outlined" />
            </Box>
            {biometricsResult.deviations?.length > 0 && (
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell sx={{ fontWeight: 700 }}>Metric</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>Z-Score</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>Current</TableCell>
                    <TableCell align="right" sx={{ fontWeight: 700 }}>Baseline Mean</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {biometricsResult.deviations.map((d, i) => (
                    <TableRow key={i}>
                      <TableCell>{d.metric.replace(/_/g, ' ')}</TableCell>
                      <TableCell align="right"><Chip size="small" color="error" label={d.z_score.toFixed(1)} /></TableCell>
                      <TableCell align="right">{d.current}</TableCell>
                      <TableCell align="right">{d.baseline_mean}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </Box>
        )}
      </ResultCard>

      {/* Payment Fraud */}
      <ResultCard title="Payment Rail Fraud Detection" icon={<PaymentIcon color="primary" />}
        result={paymentResult} engineName="payment"
        onRun={() => runScenario('payment', efmPaymentSimulate, setPaymentResult, {
          payment_rail: 'zelle', amount: 2000, destination_country: 'NG', first_time_rail: true
        })}>
        {paymentResult && (
          <Box>
            <ScoreDisplay label="Payment Fraud Score" score={paymentResult.payment_fraud_score} riskLevel={paymentResult.risk_level} icon={<PaymentIcon fontSize="small" />} />
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Table size="small">
                  <TableBody>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Payment Rail</TableCell><TableCell>{paymentResult.payment_rail?.toUpperCase()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Amount</TableCell><TableCell>${paymentResult.amount?.toLocaleString()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Per-Txn Limit</TableCell><TableCell>${paymentResult.per_txn_limit?.toLocaleString()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Daily Limit</TableCell><TableCell>${paymentResult.daily_limit?.toLocaleString()}</TableCell></TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Risk Flags</Typography>
                {paymentResult.flags?.map((f, i) => (
                  <Chip key={i} size="small" label={f.replace(/_/g, ' ')} color="error" sx={{ mr: 0.5, mb: 0.5 }} />
                ))}
              </Grid>
            </Grid>
          </Box>
        )}
      </ResultCard>

      {/* Cross-Channel Correlation */}
      <ResultCard title="Cross-Channel Fraud Correlation" icon={<DevicesIcon color="warning" />}
        result={crossChannelResult} engineName="crossChannel"
        onRun={() => runScenario('crossChannel', efmCrossChannelSimulate, setCrossChannelResult, {
          events: [
            { channel: 'mobile', event_type: 'login', amount: 0 },
            { channel: 'web', event_type: 'password_change', amount: 0 },
            { channel: 'branch', event_type: 'transfer', amount: 50000 },
            { channel: 'online', event_type: 'transfer', amount: 25000 },
          ]
        })}>
        {crossChannelResult && (
          <Box>
            <ScoreDisplay label="Correlation Score" score={crossChannelResult.correlation_score} riskLevel={crossChannelResult.risk_level} icon={<DevicesIcon fontSize="small" />} />
            <Box display="flex" gap={1} mb={2}>
              {crossChannelResult.channels_used?.map((ch, i) => (
                <Chip key={i} size="small" label={ch} color="primary" variant="outlined" />
              ))}
              <Chip size="small" label={`${crossChannelResult.event_count} events`} variant="outlined" />
            </Box>
            {crossChannelResult.patterns?.map((p, i) => (
              <Box key={i} mb={1} p={1} bgcolor="grey.50" borderRadius={1}>
                <Typography variant="body2" fontWeight={600}>{p.pattern.replace(/_/g, ' ')}</Typography>
                <Typography variant="caption" color="text.secondary">{p.detail}</Typography>
                {p.channels && <Box mt={0.5}>{p.channels.map((c, j) => <Chip key={j} size="small" label={c} sx={{ mr: 0.5 }} />)}</Box>}
              </Box>
            ))}
          </Box>
        )}
      </ResultCard>

      <Box display="flex" justifyContent="flex-end" mt={2}>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadEfmInfo} disabled={efmLoading}>
          Refresh EFM Engines
        </Button>
      </Box>
    </Box>
  );
}

/* ========================= DBF TAB (Digital Banking Fraud) ========================= */
function DBFTab({ dbfData, dbfLoading, setDbfData, setDbfLoading }) {
  const [loginResult, setLoginResult] = useState(null);
  const [sessionResult, setSessionResult] = useState(null);
  const [botResult, setBotResult] = useState(null);
  const [seResult, setSeResult] = useState(null);
  const [runningEngine, setRunningEngine] = useState(null);
  const [loginScenario, setLoginScenario] = useState('impossible_travel');
  const [botSeverity, setBotSeverity] = useState('critical');
  const [scamType, setScamType] = useState('app_fraud');

  const loadDbfInfo = async () => {
    setDbfLoading(true);
    try { const res = await getDbfInfo(); setDbfData(res.data); }
    catch { setDbfData(null); }
    finally { setDbfLoading(false); }
  };

  useEffect(() => { if (!dbfData) loadDbfInfo(); }, []);

  const runScenario = async (name, apiFn, setter, params = {}) => {
    setRunningEngine(name);
    try { const res = await apiFn(params); setter(res.data); }
    catch { setter(null); }
    finally { setRunningEngine(null); }
  };

  const riskColor = (level) => {
    if (!level) return 'default';
    if (level === 'critical') return 'error';
    if (level === 'high') return 'warning';
    if (level === 'medium') return 'info';
    return 'success';
  };

  const ScoreBar = ({ label, score, riskLevel, icon }) => (
    <Box display="flex" alignItems="center" gap={1} mb={1}>
      {icon}
      <Typography variant="body2" fontWeight={600} sx={{ minWidth: 160 }}>{label}:</Typography>
      <LinearProgress variant="determinate" value={(score || 0) * 100}
        sx={{ flex: 1, height: 10, borderRadius: 5,
          '& .MuiLinearProgress-bar': { backgroundColor: score >= 0.7 ? '#d32f2f' : score >= 0.4 ? '#ed6c02' : '#2e7d32' }
        }} />
      <Typography variant="body2" fontWeight={600} sx={{ minWidth: 50, textAlign: 'right' }}>
        {score != null ? (score * 100).toFixed(1) + '%' : '—'}
      </Typography>
      {riskLevel && <Chip size="small" label={riskLevel} color={riskColor(riskLevel)} />}
    </Box>
  );

  const ResultCard = ({ title, icon, result, onRun, engineName, children, controls }) => (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {icon}
            <Typography variant="h6" fontWeight={700}>{title}</Typography>
          </Box>
          <Box display="flex" gap={1} alignItems="center">
            {controls}
            <Button variant="contained" size="small" onClick={onRun}
              disabled={runningEngine === engineName}
              startIcon={runningEngine === engineName ? <CircularProgress size={16} /> : <PlaylistAddCheckIcon />}>
              {result ? 'Re-run' : 'Simulate'}
            </Button>
          </Box>
        </Box>
        {result && children}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Engine Status Overview */}
      <Card variant="outlined" sx={{ mb: 3, bgcolor: 'grey.50' }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <TravelExploreIcon color="primary" />
            <Typography variant="h6" fontWeight={700}>DBF Engine Status</Typography>
            <Box flex={1} />
            <Button size="small" variant="outlined" onClick={loadDbfInfo} disabled={dbfLoading}
              startIcon={dbfLoading ? <CircularProgress size={16} /> : <RefreshIcon />}>Refresh</Button>
          </Box>
          {dbfData ? (
            <Grid container spacing={1}>
              {dbfData.engines?.map((eng, i) => (
                <Grid item xs={12} sm={6} md={3} key={i}>
                  <Box display="flex" alignItems="center" gap={1} p={1} bgcolor="white" borderRadius={1}>
                    <CheckCircleIcon color="success" fontSize="small" />
                    <Box>
                      <Typography variant="body2" fontWeight={600}>{eng.name}</Typography>
                      <Typography variant="caption" color="text.secondary">{eng.description}</Typography>
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          ) : dbfLoading ? <CircularProgress size={24} /> : (
            <Alert severity="info">Click Refresh to load engine status</Alert>
          )}
          {dbfData && (
            <Box display="flex" gap={2} mt={2}>
              <Chip label={`${dbfData.total_engines} Engines Active`} color="success" size="small" icon={<CheckCircleIcon />} />
              <Chip label={`${dbfData.scam_types?.length} Scam Types`} color="warning" size="small" icon={<WarningIcon />} />
              <Chip label={`${dbfData.bot_ua_signatures?.length} Bot Signatures`} color="primary" size="small" icon={<SmartToyIcon />} />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* 1. Login Anomaly Detection */}
      <ResultCard title="Login Anomaly Detection" icon={<VpnKeyIcon color="error" />}
        result={loginResult} engineName="login"
        controls={
          <TextField select size="small" value={loginScenario} onChange={(e) => setLoginScenario(e.target.value)}
            sx={{ minWidth: 180 }}>
            <MenuItem value="impossible_travel">Impossible Travel</MenuItem>
            <MenuItem value="credential_stuffing">Credential Stuffing</MenuItem>
            <MenuItem value="unusual_time">Unusual Time + New Device</MenuItem>
          </TextField>
        }
        onRun={() => runScenario('login', dbfLoginAnomalySimulate, setLoginResult, {
          customer_id: 'CUST-LOGIN-DEMO', scenario: loginScenario
        })}>
        {loginResult && (
          <Box>
            <ScoreBar label="Login Anomaly Score" score={loginResult.login_anomaly_score}
              riskLevel={loginResult.risk_level} icon={<VpnKeyIcon fontSize="small" />} />
            <Box display="flex" gap={1} mb={2}>
              <Chip size="small" label={loginResult.is_anomalous ? 'ANOMALOUS' : 'Normal'}
                color={loginResult.is_anomalous ? 'error' : 'success'} />
              <Chip size="small" label={`${loginResult.login_history_size} logins in history`} variant="outlined" />
            </Box>
            {loginResult.flags?.map((f, i) => (
              <Box key={i} mb={1} p={1.5} bgcolor="grey.50" borderRadius={1}>
                <Box display="flex" alignItems="center" gap={1} mb={0.5}>
                  <Chip size="small" label={f.flag?.replace(/_/g, ' ')} color="error" />
                </Box>
                {f.distance_km && <Typography variant="caption">Distance: {f.distance_km.toLocaleString()} km | Speed: {f.speed_kph.toLocaleString()} kph | {f.hours_between}h between logins</Typography>}
                {f.country && <Typography variant="caption">New country: {f.country} (previous: {f.previous_countries?.join(', ')})</Typography>}
                {f.failed_attempts_10min && <Typography variant="caption">{f.failed_attempts_10min} failed attempts from {f.ip} targeting {f.unique_accounts_targeted} accounts</Typography>}
                {f.hour != null && f.typical_hours && <Typography variant="caption">Login at {f.hour}:00 — typical hours: {f.typical_hours.join(', ')}</Typography>}
                {f.device_id && <Typography variant="caption">New device: {f.device_id}</Typography>}
              </Box>
            ))}
          </Box>
        )}
      </ResultCard>

      {/* 2. Session Hijacking Detection */}
      <ResultCard title="Session Hijacking Detection" icon={<LockIcon color="warning" />}
        result={sessionResult} engineName="session"
        onRun={() => runScenario('session', dbfSessionHijackSimulate, setSessionResult, {
          session_id: 'SES-DEMO-001'
        })}>
        {sessionResult && (
          <Box>
            <ScoreBar label="Hijack Score" score={sessionResult.hijack_score}
              riskLevel={sessionResult.risk_level} icon={<LockIcon fontSize="small" />} />
            <Box display="flex" gap={1} mb={2}>
              <Chip size="small" label={sessionResult.is_hijacked ? 'HIJACKED' : 'Normal'}
                color={sessionResult.is_hijacked ? 'error' : 'success'} />
              <Chip size="small" label={`Session: ${sessionResult.session_id}`} variant="outlined" />
            </Box>
            {sessionResult.flags?.map((f, i) => (
              <Box key={i} mb={1} p={1.5} bgcolor="grey.50" borderRadius={1}>
                <Chip size="small" label={f.flag?.replace(/_/g, ' ')} color="warning" sx={{ mb: 0.5 }} />
                {f.original_ip && (
                  <Typography variant="caption" display="block">IP: {f.original_ip} &rarr; {f.current_ip}</Typography>
                )}
                {f.original_ua && (
                  <Typography variant="caption" display="block">UA: {f.original_ua} &rarr; {f.current_ua}</Typography>
                )}
                {f.active_sessions && (
                  <Typography variant="caption" display="block">{f.active_sessions} concurrent sessions from {f.unique_ips?.join(', ')}</Typography>
                )}
              </Box>
            ))}
          </Box>
        )}
      </ResultCard>

      {/* 3. Bot Detection */}
      <ResultCard title="Bot Detection" icon={<SmartToyIcon color="primary" />}
        result={botResult} engineName="bot"
        controls={
          <TextField select size="small" value={botSeverity} onChange={(e) => setBotSeverity(e.target.value)}
            sx={{ minWidth: { xs: 80, sm: 120 } }}>
            <MenuItem value="critical">Critical Bot</MenuItem>
            <MenuItem value="high">High Severity</MenuItem>
          </TextField>
        }
        onRun={() => runScenario('bot', dbfBotSimulate, setBotResult, { severity: botSeverity })}>
        {botResult && (
          <Box>
            <ScoreBar label="Bot Score" score={botResult.bot_score}
              riskLevel={botResult.risk_level} icon={<SmartToyIcon fontSize="small" />} />
            <Box display="flex" gap={1} mb={2}>
              <Chip size="small" label={botResult.is_bot ? 'BOT DETECTED' : 'Human'}
                color={botResult.is_bot ? 'error' : 'success'} />
            </Box>
            <Grid container spacing={1}>
              {botResult.flags?.map((f, i) => (
                <Grid item xs={12} sm={6} key={i}>
                  <Box p={1} bgcolor="grey.50" borderRadius={1} display="flex" alignItems="center" gap={1}>
                    <ErrorIcon color="error" fontSize="small" />
                    <Box>
                      <Typography variant="body2" fontWeight={600}>{f.flag?.replace(/_/g, ' ')}</Typography>
                      {f.matched_signature && <Typography variant="caption">Matched: {f.matched_signature}</Typography>}
                      {f.avg_click_interval_ms != null && <Typography variant="caption">{f.avg_click_interval_ms}ms avg click interval</Typography>}
                      {f.solve_time_ms != null && <Typography variant="caption">CAPTCHA solved in {f.solve_time_ms}ms</Typography>}
                      {f.requests_per_minute != null && <Typography variant="caption">{f.requests_per_minute} req/min</Typography>}
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </ResultCard>

      {/* 4. Social Engineering / Scam Detection */}
      <ResultCard title="Social Engineering / Scam Detection" icon={<WarningIcon color="error" />}
        result={seResult} engineName="se"
        controls={
          <TextField select size="small" value={scamType} onChange={(e) => setScamType(e.target.value)}
            sx={{ minWidth: 160 }}>
            <MenuItem value="app_fraud">APP Fraud</MenuItem>
            <MenuItem value="romance_scam">Romance Scam</MenuItem>
            <MenuItem value="tech_support">Tech Support Scam</MenuItem>
            <MenuItem value="impersonation">Impersonation</MenuItem>
          </TextField>
        }
        onRun={() => runScenario('se', dbfSocialEngineeringSimulate, setSeResult, { scam_type: scamType })}>
        {seResult && (
          <Box>
            <ScoreBar label="Social Engineering Score" score={seResult.social_engineering_score}
              riskLevel={seResult.risk_level} icon={<WarningIcon fontSize="small" />} />
            <Box display="flex" gap={1} mb={2}>
              <Chip size="small" label={seResult.is_suspicious ? 'SUSPICIOUS' : 'Normal'}
                color={seResult.is_suspicious ? 'error' : 'success'} />
              <Chip size="small" label={`Primary: ${seResult.primary_scam_type?.replace(/_/g, ' ')}`} color="warning" />
              <Chip size="small" label={`Amount: $${seResult.transaction_amount?.toLocaleString()}`} variant="outlined" />
            </Box>
            <Typography variant="subtitle2" fontWeight={600} gutterBottom>Scam Type Assessments</Typography>
            <Grid container spacing={1}>
              {seResult.scam_assessments && Object.entries(seResult.scam_assessments).map(([type, data]) => (
                <Grid item xs={12} sm={6} key={type}>
                  <Box p={1.5} bgcolor={data.score > 0 ? 'error.50' : 'grey.50'} borderRadius={1}
                    border={data.score > 0.5 ? '1px solid' : 'none'} borderColor="error.light">
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                      <Typography variant="body2" fontWeight={600} textTransform="capitalize">
                        {type.replace(/_/g, ' ')}
                      </Typography>
                      <Chip size="small" label={`${(data.score * 100).toFixed(0)}%`}
                        color={data.score >= 0.5 ? 'error' : data.score > 0 ? 'warning' : 'default'} />
                    </Box>
                    <Typography variant="caption" color="text.secondary">Weight: {data.weight}</Typography>
                    {data.flags?.length > 0 && (
                      <Box mt={0.5}>
                        {data.flags.map((fl, j) => (
                          <Chip key={j} size="small" label={fl.replace(/_/g, ' ')} sx={{ mr: 0.5, mb: 0.5 }}
                            color="error" variant="outlined" />
                        ))}
                      </Box>
                    )}
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Box>
        )}
      </ResultCard>

      <Box display="flex" justifyContent="flex-end" mt={2}>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadDbfInfo} disabled={dbfLoading}>
          Refresh DBF Engines
        </Button>
      </Box>
    </Box>
  );
}

export default function DataSources() {
  const [dataSources, setDataSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [testingId, setTestingId] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedSource, setSelectedSource] = useState(null);
  const [activeTab, setActiveTab] = useState(0);
  const [verifyResults, setVerifyResults] = useState(null);
  const [verifying, setVerifying] = useState(false);
  const [fieldMappings, setFieldMappings] = useState(null);
  const [fieldMappingsLoading, setFieldMappingsLoading] = useState(false);
  const [ingestionResults, setIngestionResults] = useState(null);
  const [ingestionRunning, setIngestionRunning] = useState(false);
  const [feedResults, setFeedResults] = useState(null);
  const [feedsLoading, setFeedsLoading] = useState(false);
  const [pipelineResults, setPipelineResults] = useState(null);
  const [pipelineRunning, setPipelineRunning] = useState(false);
  const [metricsData, setMetricsData] = useState(null);
  const [metricsLoading, setMetricsLoading] = useState(false);
  const [inventoryData, setInventoryData] = useState(null);
  const [inventoryLoading, setInventoryLoading] = useState(false);
  const [capabilitiesData, setCapabilitiesData] = useState(null);
  const [capabilitiesLoading, setCapabilitiesLoading] = useState(false);

  const EXPECTED_CATEGORIES = [
    'Core Banking',
    'Card / POS / ATM',
    'Wire / ACH',
    'Mobile / Online Banking',
    'KYC / Customer Data',
    'Device / IP / Geo',
    'External Feeds',
  ];

  const fetchDataSources = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getDataSources();
      setDataSources(res.data.data_sources || []);
    } catch (err) {
      setError('Failed to load data sources. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDataSources();
  }, []);

  const handleTestConnection = async (sourceId) => {
    setTestingId(sourceId);
    try {
      const res = await testDataSourceConnection(sourceId);
      setDataSources((prev) =>
        prev.map((s) =>
          s.id === sourceId
            ? { ...s, status: res.data.status, last_connected: res.data.last_connected, latency_ms: res.data.latency_ms }
            : s
        )
      );
    } catch {
      // keep current state
    } finally {
      setTestingId(null);
    }
  };

  const handleViewDetail = (source) => {
    setSelectedSource(source);
    setDetailOpen(true);
  };

  // Validation: check which expected categories are present
  const presentCategories = new Set(dataSources.map((s) => s.category));
  const missingCategories = EXPECTED_CATEGORIES.filter((c) => !presentCategories.has(c));

  const connectedCount = dataSources.filter((s) => s.status === 'connected').length;
  const degradedCount = dataSources.filter((s) => s.status === 'degraded').length;
  const disconnectedCount = dataSources.filter((s) => s.status === 'disconnected').length;

  const handleVerifyAll = async () => {
    setVerifying(true);
    try {
      const res = await verifyAllConnections();
      setVerifyResults(res.data);
    } catch {
      setVerifyResults(null);
    } finally {
      setVerifying(false);
    }
  };

  const CONN_CLASS_LABELS = {
    database: { label: 'JDBC / Database', color: '#1a237e' },
    api: { label: 'API / REST', color: '#006064' },
    file: { label: 'Flat Files / SFTP', color: '#4a148c' },
    streaming: { label: 'Streaming (Kafka / MQ)', color: '#1b5e20' },
  };

  const FREQ_LABELS = {
    'real-time': { label: 'Real-time', color: 'success', desc: 'ms / seconds latency' },
    'near-real-time': { label: 'Near Real-time', color: 'info', desc: 'seconds / minutes' },
    batch: { label: 'Batch', color: 'warning', desc: 'hourly / daily load' },
  };

  const formatDelay = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    if (seconds < 86400) return `${(seconds / 3600).toFixed(1)}h`;
    return `${(seconds / 86400).toFixed(1)}d`;
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Box>
          <Typography variant="h4">Data Sources Configuration</Typography>
          <Typography variant="body2" color="text.secondary" mt={0.5}>
            Administration &rarr; Data Sources &mdash; Manage and monitor all configured integrations
          </Typography>
        </Box>
        <Box display="flex" gap={1}>
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchDataSources} disabled={loading}>
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)}>
          <Tab icon={<StorageIcon />} iconPosition="start" label="Data Sources" />
          <Tab icon={<VerifiedUserIcon />} iconPosition="start" label="Connection Details" />
          <Tab icon={<AccountTreeIcon />} iconPosition="start" label="Field Mapping" />
          <Tab icon={<AssessmentIcon />} iconPosition="start" label="Data Quality" />
          <Tab icon={<GppGoodIcon />} iconPosition="start" label="External Feeds" />
          <Tab icon={<RocketLaunchIcon />} iconPosition="start" label="Pipeline Test" />
          <Tab icon={<MonitorHeartIcon />} iconPosition="start" label="Monitoring" />
          <Tab icon={<DescriptionIcon />} iconPosition="start" label="Documentation" />
          <Tab icon={<SecurityIcon />} iconPosition="start" label="Capabilities" />
        </Tabs>
      </Paper>

      {/* ===================== TAB 0: Data Sources (original) ===================== */}
      {activeTab === 0 && (
        <>
          {/* Validation Banner */}
          {!loading && missingCategories.length === 0 && (
            <Alert severity="success" sx={{ mb: 2 }} icon={<CheckCircleIcon />}>
              <strong>All expected data source categories are configured.</strong> No missing sources detected.
            </Alert>
          )}
          {!loading && missingCategories.length > 0 && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              <strong>Missing data source categories:</strong> {missingCategories.join(', ')}.
              Please configure the missing integrations.
            </Alert>
          )}

          {/* Summary Cards */}
          <Grid container spacing={2} mb={3}>
            <Grid item xs={12} sm={6} md={3}>
              <Card><CardContent sx={{ textAlign: 'center' }}>
                <StorageIcon sx={{ fontSize: 36, color: 'primary.main', mb: 1 }} />
                <Typography variant="h4">{dataSources.length}</Typography>
                <Typography variant="body2" color="text.secondary">Total Sources</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card><CardContent sx={{ textAlign: 'center' }}>
                <CheckCircleIcon sx={{ fontSize: 36, color: 'success.main', mb: 1 }} />
                <Typography variant="h4" color="success.main">{connectedCount}</Typography>
                <Typography variant="body2" color="text.secondary">Connected</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card><CardContent sx={{ textAlign: 'center' }}>
                <WarningIcon sx={{ fontSize: 36, color: 'warning.main', mb: 1 }} />
                <Typography variant="h4" color="warning.main">{degradedCount}</Typography>
                <Typography variant="body2" color="text.secondary">Degraded</Typography>
              </CardContent></Card>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Card><CardContent sx={{ textAlign: 'center' }}>
                <ErrorIcon sx={{ fontSize: 36, color: 'error.main', mb: 1 }} />
                <Typography variant="h4" color="error.main">{disconnectedCount}</Typography>
                <Typography variant="body2" color="text.secondary">Disconnected</Typography>
              </CardContent></Card>
            </Grid>
          </Grid>

          {/* Expected Categories Checklist */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>Source Categories Checklist</Typography>
              <Grid container spacing={1}>
                {EXPECTED_CATEGORIES.map((cat) => {
                  const present = presentCategories.has(cat);
                  const sources = dataSources.filter((s) => s.category === cat);
                  return (
                    <Grid item xs={12} sm={6} md={3} key={cat}>
                      <Box display="flex" alignItems="center" gap={1} p={1} borderRadius={1}
                        sx={{ bgcolor: present ? 'success.50' : 'error.50', border: 1, borderColor: present ? 'success.light' : 'error.light' }}>
                        {present ? <CheckCircleIcon color="success" fontSize="small" /> : <ErrorIcon color="error" fontSize="small" />}
                        <Box>
                          <Typography variant="body2" fontWeight={600}>{cat}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {present ? `${sources.length} source(s)` : 'Not configured'}
                          </Typography>
                        </Box>
                      </Box>
                    </Grid>
                  );
                })}
              </Grid>
            </CardContent>
          </Card>

          {/* Data Sources Table */}
          {loading ? (
            <Box display="flex" justifyContent="center" py={6}><CircularProgress /></Box>
          ) : error ? (
            <Alert severity="error">{error}</Alert>
          ) : (
            <TableContainer component={Paper}>
              <Table>
                <TableHead>
                  <TableRow sx={{ bgcolor: 'primary.main' }}>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Source Name</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Category</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Type</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Status</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Last Connected</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Latency</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }}>Records/Day</TableCell>
                    <TableCell sx={{ color: 'white', fontWeight: 600 }} align="center">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {dataSources.map((source) => {
                    const statusCfg = STATUS_CONFIG[source.status] || STATUS_CONFIG.disconnected;
                    return (
                      <TableRow key={source.id} hover>
                        <TableCell>
                          <Box display="flex" alignItems="center" gap={1}>
                            <StorageIcon fontSize="small" sx={{ color: CATEGORY_COLORS[source.category] || 'grey' }} />
                            <Box>
                              <Typography variant="body2" fontWeight={600}>{source.name}</Typography>
                              <Typography variant="caption" color="text.secondary">{source.description}</Typography>
                            </Box>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip label={source.category} size="small"
                            sx={{ bgcolor: CATEGORY_COLORS[source.category] || '#666', color: 'white', fontWeight: 500 }} />
                        </TableCell>
                        <TableCell><Typography variant="body2">{source.connection_type}</Typography></TableCell>
                        <TableCell>
                          <Chip icon={statusCfg.icon} label={statusCfg.label} size="small" color={statusCfg.color} variant="outlined" />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {source.last_connected ? new Date(source.last_connected).toLocaleString() : 'Never'}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{source.latency_ms != null ? `${source.latency_ms} ms` : '—'}</Typography>
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">{source.records_per_day?.toLocaleString() || '—'}</Typography>
                        </TableCell>
                        <TableCell align="center">
                          <Tooltip title="Test Connection">
                            <span>
                              <IconButton size="small" onClick={() => handleTestConnection(source.id)} disabled={testingId === source.id}>
                                {testingId === source.id ? <CircularProgress size={18} /> : <SyncIcon fontSize="small" />}
                              </IconButton>
                            </span>
                          </Tooltip>
                          <Tooltip title="View Details">
                            <IconButton size="small" onClick={() => handleViewDetail(source)}>
                              <InfoOutlinedIcon fontSize="small" />
                            </IconButton>
                          </Tooltip>
                        </TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </>
      )}

      {/* ===================== TAB 1: Connection Details ===================== */}
      {activeTab === 1 && (
        <>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Typography variant="h6">Step 2: Check Connection Details</Typography>
            <Button variant="contained" startIcon={verifying ? <CircularProgress size={18} color="inherit" /> : <PlaylistAddCheckIcon />}
              onClick={handleVerifyAll} disabled={verifying}>
              {verifying ? 'Verifying...' : 'Verify All Connections'}
            </Button>
          </Box>

          {/* Verification summary banner */}
          {verifyResults && (
            <Alert severity={verifyResults.all_passed ? 'success' : 'warning'} sx={{ mb: 2 }}
              icon={verifyResults.all_passed ? <CheckCircleIcon /> : <WarningIcon />}>
              <strong>
                {verifyResults.all_passed
                  ? `All ${verifyResults.total_sources} connections verified — no broken connections or long delays.`
                  : `${verifyResults.failed} of ${verifyResults.total_sources} sources have issues.`}
              </strong>
              <Typography variant="caption" display="block">
                Verified at {new Date(verifyResults.verification_timestamp).toLocaleString()}
              </Typography>
            </Alert>
          )}

          {/* Issues list */}
          {verifyResults && verifyResults.issues.length > 0 && (
            <Card sx={{ mb: 2, borderLeft: '4px solid', borderColor: 'error.main' }}>
              <CardContent>
                <Typography variant="subtitle2" color="error" gutterBottom>Issues Found</Typography>
                {verifyResults.issues.map((issue, idx) => (
                  <Box key={idx} display="flex" alignItems="center" gap={1} mb={0.5}>
                    <ErrorIcon color="error" fontSize="small" />
                    <Typography variant="body2">
                      <strong>{issue.name}</strong>: {issue.issue}
                    </Typography>
                  </Box>
                ))}
              </CardContent>
            </Card>
          )}

          {/* Per-source accordion cards */}
          {(verifyResults ? verifyResults.results : dataSources).map((src) => {
            const connClass = CONN_CLASS_LABELS[src.connection_class] || { label: src.connection_type, color: '#666' };
            const freq = FREQ_LABELS[src.update_frequency] || { label: src.update_frequency || '—', color: 'default', desc: '' };
            const passed = src.check_passed !== undefined ? src.check_passed : true;
            const credsOk = src.credentials_valid !== undefined ? src.credentials_valid : true;
            const permsOk = src.permissions_verified !== undefined ? src.permissions_verified : true;
            const syncOk = src.sync_healthy !== undefined ? src.sync_healthy : (src.sync_status === 'ok');

            return (
              <Accordion key={src.source_id || src.id} defaultExpanded={!passed} sx={{ mb: 1 }}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={2} width="100%">
                    {passed ? <CheckCircleIcon color="success" /> : <WarningIcon color="warning" />}
                    <Box flexGrow={1}>
                      <Typography variant="subtitle2">{src.name}</Typography>
                      <Typography variant="caption" color="text.secondary">{src.category}</Typography>
                    </Box>
                    <Chip label={connClass.label} size="small"
                      sx={{ bgcolor: connClass.color, color: 'white', mr: 1 }} />
                    <Chip label={freq.label} size="small" color={freq.color} variant="outlined" />
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {/* Connection Type */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined" sx={{ height: '100%' }}>
                        <CardContent>
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <StorageIcon color="primary" fontSize="small" />
                            <Typography variant="caption" fontWeight={600}>Connection Type</Typography>
                          </Box>
                          <Typography variant="body2" fontWeight={600}>{src.connection_type}</Typography>
                          <Typography variant="caption" color="text.secondary">{connClass.label}</Typography>
                          <Box mt={1}>
                            <Typography variant="caption" color="text.secondary">Endpoint</Typography>
                            <Typography variant="caption" fontFamily="monospace" display="block"
                              sx={{ bgcolor: 'grey.100', p: 0.5, borderRadius: 0.5, wordBreak: 'break-all' }}>
                              {src.endpoint || '—'}
                            </Typography>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>

                    {/* Authentication & Access */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined" sx={{ height: '100%' }}>
                        <CardContent>
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <LockIcon color="primary" fontSize="small" />
                            <Typography variant="caption" fontWeight={600}>Authentication & Access</Typography>
                          </Box>
                          <Typography variant="body2" fontWeight={600}>{src.auth_method || 'N/A'}</Typography>
                          <Box display="flex" alignItems="center" gap={0.5} mt={1}>
                            {credsOk ? <CheckCircleIcon color="success" sx={{ fontSize: 16 }} /> : <ErrorIcon color="error" sx={{ fontSize: 16 }} />}
                            <Typography variant="body2">Credentials {credsOk ? 'Valid' : 'Invalid / Expired'}</Typography>
                          </Box>
                          <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
                            {permsOk ? <CheckCircleIcon color="success" sx={{ fontSize: 16 }} /> : <ErrorIcon color="error" sx={{ fontSize: 16 }} />}
                            <Typography variant="body2">
                              Permissions: {src.permission_level === 'full_read' ? 'Full Read Access' : (src.permission_level || 'Unknown')}
                            </Typography>
                          </Box>
                        </CardContent>
                      </Card>
                    </Grid>

                    {/* Update Frequency */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined" sx={{ height: '100%' }}>
                        <CardContent>
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <ScheduleIcon color="primary" fontSize="small" />
                            <Typography variant="caption" fontWeight={600}>Update Frequency</Typography>
                          </Box>
                          <Chip label={freq.label} size="small" color={freq.color} sx={{ mb: 1 }} />
                          <Typography variant="body2">{src.update_interval_display || '—'}</Typography>
                          {freq.desc && (
                            <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                              {freq.desc}
                            </Typography>
                          )}
                        </CardContent>
                      </Card>
                    </Grid>

                    {/* Last Sync */}
                    <Grid item xs={12} sm={6} md={3}>
                      <Card variant="outlined" sx={{ height: '100%' }}>
                        <CardContent>
                          <Box display="flex" alignItems="center" gap={1} mb={1}>
                            <SpeedIcon color="primary" fontSize="small" />
                            <Typography variant="caption" fontWeight={600}>Sync Status</Typography>
                          </Box>
                          <Box display="flex" alignItems="center" gap={0.5}>
                            {syncOk ? <CheckCircleIcon color="success" sx={{ fontSize: 16 }} /> : <WarningIcon color="warning" sx={{ fontSize: 16 }} />}
                            <Typography variant="body2" fontWeight={600}>
                              {syncOk ? 'On schedule' : 'Delayed'}
                            </Typography>
                          </Box>
                          <Typography variant="caption" color="text.secondary" display="block" mt={0.5}>
                            Last sync: {src.last_sync ? new Date(src.last_sync).toLocaleString() : 'Never'}
                          </Typography>
                          {src.sync_delay_seconds != null && (
                            <Typography variant="caption" color="text.secondary" display="block">
                              Delay: {formatDelay(src.sync_delay_seconds)} (max: {formatDelay(src.expected_max_delay_seconds || 0)})
                            </Typography>
                          )}
                          {src.sync_records_last != null && (
                            <Typography variant="caption" color="text.secondary" display="block">
                              Last batch: {src.sync_records_last.toLocaleString()} records
                            </Typography>
                          )}
                          <Typography variant="caption" color="text.secondary" display="block">
                            Latency: {src.latency_ms != null ? `${src.latency_ms} ms` : '—'}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>

                    {/* Per-source issues */}
                    {src.issues && src.issues.length > 0 && (
                      <Grid item xs={12}>
                        <Alert severity="warning" variant="outlined">
                          {src.issues.map((iss, i) => (
                            <Typography key={i} variant="body2">• {iss}</Typography>
                          ))}
                        </Alert>
                      </Grid>
                    )}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            );
          })}
        </>
      )}

      {/* ===================== TAB 2: Field Mapping ===================== */}
      {activeTab === 2 && (
        <FieldMappingTab
          fieldMappings={fieldMappings}
          fieldMappingsLoading={fieldMappingsLoading}
          setFieldMappings={setFieldMappings}
          setFieldMappingsLoading={setFieldMappingsLoading}
        />
      )}

      {/* ===================== TAB 3: Data Quality ===================== */}
      {activeTab === 3 && (
        <DataQualityTab
          ingestionResults={ingestionResults}
          ingestionRunning={ingestionRunning}
          setIngestionResults={setIngestionResults}
          setIngestionRunning={setIngestionRunning}
        />
      )}

      {/* ===================== TAB 4: External Feeds ===================== */}
      {activeTab === 4 && (
        <ExternalFeedsTab
          feedResults={feedResults}
          feedsLoading={feedsLoading}
          setFeedResults={setFeedResults}
          setFeedsLoading={setFeedsLoading}
        />
      )}

      {/* ===================== TAB 5: Pipeline Test ===================== */}
      {activeTab === 5 && (
        <PipelineTestTab
          pipelineResults={pipelineResults}
          pipelineRunning={pipelineRunning}
          setPipelineResults={setPipelineResults}
          setPipelineRunning={setPipelineRunning}
        />
      )}

      {/* ===================== TAB 6: Monitoring ===================== */}
      {activeTab === 6 && (
        <MonitoringTab
          metricsData={metricsData}
          metricsLoading={metricsLoading}
          setMetricsData={setMetricsData}
          setMetricsLoading={setMetricsLoading}
        />
      )}

      {/* ===================== TAB 7: Documentation ===================== */}
      {activeTab === 7 && (
        <DocumentationTab
          inventoryData={inventoryData}
          inventoryLoading={inventoryLoading}
          setInventoryData={setInventoryData}
          setInventoryLoading={setInventoryLoading}
        />
      )}

      {/* ===================== TAB 8: Capabilities ===================== */}
      {activeTab === 8 && (
        <CapabilitiesTab
          capabilitiesData={capabilitiesData}
          capabilitiesLoading={capabilitiesLoading}
          setCapabilitiesData={setCapabilitiesData}
          setCapabilitiesLoading={setCapabilitiesLoading}
        />
      )}

      {/* Detail Dialog */}
      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth>
        {selectedSource && (
          <>
            <DialogTitle>
              <Box display="flex" alignItems="center" gap={1}>
                <StorageIcon color="primary" />
                {selectedSource.name}
              </Box>
            </DialogTitle>
            <DialogContent dividers>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Category</Typography>
                  <Typography variant="body2" fontWeight={600}>{selectedSource.category}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Connection Type</Typography>
                  <Typography variant="body2" fontWeight={600}>{selectedSource.connection_type}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Status</Typography>
                  <Box mt={0.5}>
                    <Chip
                      icon={STATUS_CONFIG[selectedSource.status]?.icon}
                      label={STATUS_CONFIG[selectedSource.status]?.label}
                      size="small"
                      color={STATUS_CONFIG[selectedSource.status]?.color}
                    />
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Latency</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {selectedSource.latency_ms != null ? `${selectedSource.latency_ms} ms` : 'N/A'}
                  </Typography>
                </Grid>

                <Grid item xs={12}><Divider /></Grid>

                {/* Auth & Permissions section */}
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Auth Method</Typography>
                  <Typography variant="body2" fontWeight={600}>{selectedSource.auth_method || 'N/A'}</Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Credentials</Typography>
                  <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
                    {selectedSource.credentials_valid
                      ? <><CheckCircleIcon color="success" sx={{ fontSize: 16 }} /><Typography variant="body2">Valid</Typography></>
                      : <><ErrorIcon color="error" sx={{ fontSize: 16 }} /><Typography variant="body2">Invalid</Typography></>}
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Permissions</Typography>
                  <Box display="flex" alignItems="center" gap={0.5} mt={0.5}>
                    {selectedSource.permissions_verified
                      ? <><CheckCircleIcon color="success" sx={{ fontSize: 16 }} /><Typography variant="body2">Full Read Access</Typography></>
                      : <><WarningIcon color="warning" sx={{ fontSize: 16 }} /><Typography variant="body2">Not Verified</Typography></>}
                  </Box>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Update Frequency</Typography>
                  <Typography variant="body2" fontWeight={600}>{selectedSource.update_interval_display || selectedSource.update_frequency || 'N/A'}</Typography>
                </Grid>

                <Grid item xs={12}><Divider /></Grid>

                {/* Sync info */}
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Last Sync</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {selectedSource.last_sync ? new Date(selectedSource.last_sync).toLocaleString() : 'Never'}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Records / Day</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {selectedSource.records_per_day?.toLocaleString() || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Last Batch Records</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {selectedSource.sync_records_last?.toLocaleString() || 'N/A'}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="caption" color="text.secondary">Last Connected</Typography>
                  <Typography variant="body2" fontWeight={600}>
                    {selectedSource.last_connected ? new Date(selectedSource.last_connected).toLocaleString() : 'Never'}
                  </Typography>
                </Grid>

                <Grid item xs={12}><Divider /></Grid>

                <Grid item xs={12}>
                  <Typography variant="caption" color="text.secondary">Description</Typography>
                  <Typography variant="body2">{selectedSource.description}</Typography>
                </Grid>
                <Grid item xs={12}>
                  <Typography variant="caption" color="text.secondary">Endpoint / Host</Typography>
                  <Typography variant="body2" fontFamily="monospace" sx={{ bgcolor: 'grey.100', p: 1, borderRadius: 1, wordBreak: 'break-all' }}>
                    {selectedSource.endpoint}
                  </Typography>
                </Grid>
                {selectedSource.data_fields && (
                  <Grid item xs={12}>
                    <Typography variant="caption" color="text.secondary">Data Fields</Typography>
                    <Box display="flex" flexWrap="wrap" gap={0.5} mt={0.5}>
                      {selectedSource.data_fields.map((f) => (
                        <Chip key={f} label={f} size="small" variant="outlined" />
                      ))}
                    </Box>
                  </Grid>
                )}
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={() => setDetailOpen(false)}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
}

/* ========================= PMF TAB (Payments Fraud) ========================= */
function PMFTab({ pmfData, pmfLoading, setPmfData, setPmfLoading }) {
  const [achResult, setAchResult] = useState(null);
  const [wireResult, setWireResult] = useState(null);
  const [rtpResult, setRtpResult] = useState(null);
  const [cnpResult, setCnpResult] = useState(null);
  const [checkResult, setCheckResult] = useState(null);
  const [runningEngine, setRunningEngine] = useState(null);
  const [achScenario, setAchScenario] = useState('unauthorized_debit');
  const [wireScenario, setWireScenario] = useState('bec_attack');
  const [rtpScenario, setRtpScenario] = useState('push_payment_scam');
  const [cnpScenario, setCnpScenario] = useState('velocity_attack');
  const [checkScenario, setCheckScenario] = useState('altered_check');

  const loadPmfInfo = async () => {
    setPmfLoading(true);
    try { const res = await getPmfInfo(); setPmfData(res.data); }
    catch { setPmfData(null); }
    finally { setPmfLoading(false); }
  };

  useEffect(() => { if (!pmfData) loadPmfInfo(); }, []);

  const runScenario = async (name, apiFn, setter, params = {}) => {
    setRunningEngine(name);
    try { const res = await apiFn(params); setter(res.data); }
    catch { setter(null); }
    finally { setRunningEngine(null); }
  };

  const riskColor = (level) => {
    if (!level) return 'default';
    if (level === 'critical') return 'error';
    if (level === 'high') return 'warning';
    if (level === 'medium') return 'info';
    return 'success';
  };

  const ScoreBar = ({ label, score, riskLevel, icon }) => (
    <Box display="flex" alignItems="center" gap={1} mb={1}>
      {icon}
      <Typography variant="body2" fontWeight={600} sx={{ minWidth: 160 }}>{label}:</Typography>
      <LinearProgress variant="determinate" value={(score || 0) * 100}
        sx={{ flex: 1, height: 10, borderRadius: 5,
          '& .MuiLinearProgress-bar': { backgroundColor: score >= 0.7 ? '#d32f2f' : score >= 0.4 ? '#ed6c02' : '#2e7d32' }
        }} />
      <Typography variant="body2" fontWeight={600} sx={{ minWidth: 50, textAlign: 'right' }}>
        {score != null ? (score * 100).toFixed(1) + '%' : '—'}
      </Typography>
      {riskLevel && <Chip size="small" label={riskLevel} color={riskColor(riskLevel)} />}
    </Box>
  );

  const ResultCard = ({ title, icon, result, onRun, engineName, children, controls }) => (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box display="flex" alignItems="center" gap={1}>
            {icon}
            <Typography variant="h6" fontWeight={700}>{title}</Typography>
          </Box>
          <Box display="flex" alignItems="center" gap={1}>
            {controls}
            <Button variant="contained" size="small" onClick={onRun}
              disabled={runningEngine === engineName}
              startIcon={runningEngine === engineName ? <CircularProgress size={16} /> : <PlaylistAddCheckIcon />}>
              {result ? 'Re-run' : 'Simulate'}
            </Button>
          </Box>
        </Box>
        {result && children}
      </CardContent>
    </Card>
  );

  return (
    <Box>
      {/* Engine Status Overview */}
      <Card variant="outlined" sx={{ mb: 3, bgcolor: 'grey.50' }}>
        <CardContent>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <PaymentIcon color="primary" />
            <Typography variant="h6" fontWeight={700}>PMF Engine Status</Typography>
            <Box flex={1} />
            <Button size="small" variant="outlined" onClick={loadPmfInfo} disabled={pmfLoading}
              startIcon={pmfLoading ? <CircularProgress size={16} /> : <RefreshIcon />}>Refresh</Button>
          </Box>
          {pmfData ? (
            <Grid container spacing={1}>
              {pmfData.engines?.map((eng, i) => (
                <Grid item xs={12} sm={6} md={4} key={i}>
                  <Box display="flex" alignItems="center" gap={1} p={1} bgcolor="white" borderRadius={1}>
                    <CheckCircleIcon color="success" fontSize="small" />
                    <Box>
                      <Typography variant="body2" fontWeight={600}>{eng.name}</Typography>
                      <Typography variant="caption" color="text.secondary">{eng.description}</Typography>
                    </Box>
                  </Box>
                </Grid>
              ))}
            </Grid>
          ) : pmfLoading ? <CircularProgress size={24} /> : (
            <Alert severity="info">Click Refresh to load engine status</Alert>
          )}
          {pmfData && (
            <Box display="flex" gap={2} mt={2}>
              <Chip label={`${pmfData.total_engines} Engines Active`} color="success" size="small" icon={<CheckCircleIcon />} />
              <Chip label={`${pmfData.payment_channels?.length} Payment Channels`} color="primary" size="small" icon={<PaymentIcon />} />
            </Box>
          )}
        </CardContent>
      </Card>

      {/* ACH Fraud */}
      <ResultCard title="ACH Fraud Detection" icon={<AccountTreeIcon color="error" />}
        result={achResult} engineName="ach"
        controls={
          <TextField select size="small" value={achScenario} onChange={(e) => setAchScenario(e.target.value)}
            sx={{ minWidth: 180 }}>
            <MenuItem value="unauthorized_debit">Unauthorized Debit</MenuItem>
            <MenuItem value="velocity_spike">Velocity Spike</MenuItem>
            <MenuItem value="return_code_risk">Return Code Risk</MenuItem>
          </TextField>
        }
        onRun={() => runScenario('ach', pmfAchSimulate, setAchResult, { scenario: achScenario })}>
        {achResult && (
          <Box>
            <ScoreBar label="ACH Fraud Score" score={achResult.ach_fraud_score} riskLevel={achResult.risk_level}
              icon={<AccountTreeIcon fontSize="small" />} />
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Table size="small">
                  <TableBody>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Customer</TableCell><TableCell>{achResult.customer_id}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Amount</TableCell><TableCell>${achResult.transaction_amount?.toLocaleString()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Direction</TableCell><TableCell>{achResult.direction}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Suspicious</TableCell>
                      <TableCell><Chip size="small" label={achResult.is_suspicious ? 'Yes' : 'No'}
                        color={achResult.is_suspicious ? 'error' : 'success'} /></TableCell></TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Risk Flags</Typography>
                {achResult.flags?.map((f, i) => (
                  <Box key={i} mb={1} p={1} bgcolor="grey.50" borderRadius={1}>
                    <Typography variant="body2" fontWeight={600}>{f.flag.replace(/_/g, ' ')}</Typography>
                    {f.amount && <Typography variant="caption" color="text.secondary">Amount: ${f.amount.toLocaleString()}</Typography>}
                    {f.count_24h && <Typography variant="caption" color="text.secondary"> | Count: {f.count_24h}/{f.limit}</Typography>}
                    {f.worst_code && <Typography variant="caption" color="text.secondary"> | Worst: {f.worst_code}</Typography>}
                  </Box>
                ))}
              </Grid>
            </Grid>
          </Box>
        )}
      </ResultCard>

      {/* Wire Fraud */}
      <ResultCard title="Wire Fraud Detection" icon={<TrendingUpIcon color="warning" />}
        result={wireResult} engineName="wire"
        controls={
          <TextField select size="small" value={wireScenario} onChange={(e) => setWireScenario(e.target.value)}
            sx={{ minWidth: 180 }}>
            <MenuItem value="bec_attack">BEC Attack</MenuItem>
            <MenuItem value="high_risk_country">High-Risk Country</MenuItem>
          </TextField>
        }
        onRun={() => runScenario('wire', pmfWireSimulate, setWireResult, { scenario: wireScenario })}>
        {wireResult && (
          <Box>
            <ScoreBar label="Wire Fraud Score" score={wireResult.wire_fraud_score} riskLevel={wireResult.risk_level}
              icon={<TrendingUpIcon fontSize="small" />} />
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Table size="small">
                  <TableBody>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Customer</TableCell><TableCell>{wireResult.customer_id}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Amount</TableCell><TableCell>${wireResult.transaction_amount?.toLocaleString()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Beneficiary Country</TableCell><TableCell>{wireResult.beneficiary_country}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Suspicious</TableCell>
                      <TableCell><Chip size="small" label={wireResult.is_suspicious ? 'Yes' : 'No'}
                        color={wireResult.is_suspicious ? 'error' : 'success'} /></TableCell></TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Risk Flags</Typography>
                {wireResult.flags?.map((f, i) => (
                  <Box key={i} mb={1} p={1} bgcolor="grey.50" borderRadius={1}>
                    <Typography variant="body2" fontWeight={600}>{f.flag.replace(/_/g, ' ')}</Typography>
                    {f.matched_signals && <Typography variant="caption" color="text.secondary">Signals: {f.matched_signals.join(', ')}</Typography>}
                    {f.country && <Typography variant="caption" color="text.secondary">Country: {f.country}</Typography>}
                    {f.multiplier && <Typography variant="caption" color="text.secondary"> | {f.multiplier}x baseline</Typography>}
                  </Box>
                ))}
              </Grid>
            </Grid>
          </Box>
        )}
      </ResultCard>

      {/* RTP/Zelle Fraud */}
      <ResultCard title="RTP / Zelle Fraud Detection" icon={<SpeedIcon color="primary" />}
        result={rtpResult} engineName="rtp"
        controls={
          <TextField select size="small" value={rtpScenario} onChange={(e) => setRtpScenario(e.target.value)}
            sx={{ minWidth: 180 }}>
            <MenuItem value="push_payment_scam">Push-Payment Scam</MenuItem>
            <MenuItem value="velocity_fanout">Velocity Fan-out</MenuItem>
          </TextField>
        }
        onRun={() => runScenario('rtp', pmfRtpZelleSimulate, setRtpResult, { scenario: rtpScenario })}>
        {rtpResult && (
          <Box>
            <ScoreBar label="RTP/Zelle Score" score={rtpResult.rtp_fraud_score} riskLevel={rtpResult.risk_level}
              icon={<SpeedIcon fontSize="small" />} />
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Table size="small">
                  <TableBody>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Customer</TableCell><TableCell>{rtpResult.customer_id}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Amount</TableCell><TableCell>${rtpResult.transaction_amount?.toLocaleString()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Channel</TableCell><TableCell>{rtpResult.channel?.toUpperCase()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Suspicious</TableCell>
                      <TableCell><Chip size="small" label={rtpResult.is_suspicious ? 'Yes' : 'No'}
                        color={rtpResult.is_suspicious ? 'error' : 'success'} /></TableCell></TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Risk Flags</Typography>
                {rtpResult.flags?.map((f, i) => (
                  <Box key={i} mb={1} p={1} bgcolor="grey.50" borderRadius={1}>
                    <Typography variant="body2" fontWeight={600}>{f.flag.replace(/_/g, ' ')}</Typography>
                    {f.matched_signals && <Typography variant="caption" color="text.secondary">Signals: {f.matched_signals.join(', ')}</Typography>}
                    {f.count_1h && <Typography variant="caption" color="text.secondary">Count: {f.count_1h}/{f.limit}</Typography>}
                    {f.unique_recipients_1h && <Typography variant="caption" color="text.secondary">Recipients: {f.unique_recipients_1h}</Typography>}
                    {f.account_age_days != null && <Typography variant="caption" color="text.secondary">Account age: {f.account_age_days}d</Typography>}
                  </Box>
                ))}
              </Grid>
            </Grid>
          </Box>
        )}
      </ResultCard>

      {/* CNP Fraud */}
      <ResultCard title="Card-Not-Present (CNP) Fraud Detection" icon={<CreditCardIcon color="error" />}
        result={cnpResult} engineName="cnp"
        controls={
          <TextField select size="small" value={cnpScenario} onChange={(e) => setCnpScenario(e.target.value)}
            sx={{ minWidth: 180 }}>
            <MenuItem value="velocity_attack">Velocity Attack</MenuItem>
            <MenuItem value="geo_mismatch">Geo Mismatch</MenuItem>
          </TextField>
        }
        onRun={() => runScenario('cnp', pmfCnpSimulate, setCnpResult, { scenario: cnpScenario })}>
        {cnpResult && (
          <Box>
            <ScoreBar label="CNP Fraud Score" score={cnpResult.cnp_fraud_score} riskLevel={cnpResult.risk_level}
              icon={<CreditCardIcon fontSize="small" />} />
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Table size="small">
                  <TableBody>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Card Hash</TableCell><TableCell>{cnpResult.card_hash}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Amount</TableCell><TableCell>${cnpResult.transaction_amount?.toLocaleString()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Suspicious</TableCell>
                      <TableCell><Chip size="small" label={cnpResult.is_suspicious ? 'Yes' : 'No'}
                        color={cnpResult.is_suspicious ? 'error' : 'success'} /></TableCell></TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Risk Flags</Typography>
                {cnpResult.flags?.map((f, i) => (
                  <Box key={i} mb={1} p={1} bgcolor="grey.50" borderRadius={1}>
                    <Typography variant="body2" fontWeight={600}>{f.flag.replace(/_/g, ' ')}</Typography>
                    {f.avs_code && <Typography variant="caption" color="text.secondary">AVS: {f.avs_code}</Typography>}
                    {f.small_auth_count_10min && <Typography variant="caption" color="text.secondary">Small auths: {f.small_auth_count_10min}</Typography>}
                    {f.unique_cards_10min && <Typography variant="caption" color="text.secondary">BIN {f.bin_prefix}: {f.unique_cards_10min} cards</Typography>}
                    {f.billing_country && <Typography variant="caption" color="text.secondary">Billing: {f.billing_country} → Shipping: {f.shipping_country}</Typography>}
                  </Box>
                ))}
              </Grid>
            </Grid>
          </Box>
        )}
      </ResultCard>

      {/* Check Fraud */}
      <ResultCard title="Check Fraud (Image Analysis)" icon={<DescriptionIcon color="secondary" />}
        result={checkResult} engineName="check"
        controls={
          <TextField select size="small" value={checkScenario} onChange={(e) => setCheckScenario(e.target.value)}
            sx={{ minWidth: 180 }}>
            <MenuItem value="altered_check">Altered Check</MenuItem>
            <MenuItem value="counterfeit">Counterfeit</MenuItem>
            <MenuItem value="duplicate">Duplicate</MenuItem>
          </TextField>
        }
        onRun={() => runScenario('check', pmfCheckSimulate, setCheckResult, { scenario: checkScenario })}>
        {checkResult && (
          <Box>
            <ScoreBar label="Check Fraud Score" score={checkResult.check_fraud_score} riskLevel={checkResult.risk_level}
              icon={<DescriptionIcon fontSize="small" />} />
            <Grid container spacing={2} mt={1}>
              <Grid item xs={6}>
                <Table size="small">
                  <TableBody>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Account</TableCell><TableCell>{checkResult.account_id}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Check Amount</TableCell><TableCell>${checkResult.check_amount?.toLocaleString()}</TableCell></TableRow>
                    <TableRow><TableCell sx={{ fontWeight: 600 }}>Suspicious</TableCell>
                      <TableCell><Chip size="small" label={checkResult.is_suspicious ? 'Yes' : 'No'}
                        color={checkResult.is_suspicious ? 'error' : 'success'} /></TableCell></TableRow>
                  </TableBody>
                </Table>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>Risk Flags</Typography>
                {checkResult.flags?.map((f, i) => (
                  <Box key={i} mb={1} p={1} bgcolor="grey.50" borderRadius={1}>
                    <Typography variant="body2" fontWeight={600}>{f.flag.replace(/_/g, ' ')}</Typography>
                    {f.confidence != null && <Typography variant="caption" color="text.secondary">Confidence: {(f.confidence * 100).toFixed(0)}%</Typography>}
                    {f.car_amount != null && <Typography variant="caption" color="text.secondary">CAR: ${f.car_amount} vs LAR: ${f.lar_amount}</Typography>}
                    {f.indicators && <Typography variant="caption" color="text.secondary">Indicators: {f.indicators.join(', ')}</Typography>}
                    {f.details && <Typography variant="caption" color="text.secondary">Details: {f.details.join(', ')}</Typography>}
                    {f.original_account && <Typography variant="caption" color="text.secondary">Original: {f.original_account}</Typography>}
                    {f.expected_routing && <Typography variant="caption" color="text.secondary">Expected: {f.expected_routing} → Actual: {f.actual_routing}</Typography>}
                  </Box>
                ))}
              </Grid>
            </Grid>
          </Box>
        )}
      </ResultCard>

      <Box display="flex" justifyContent="flex-end" mt={2}>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadPmfInfo} disabled={pmfLoading}>
          Refresh PMF Engines
        </Button>
      </Box>
    </Box>
  );
}

export { CapabilitiesTab, CDDTab, WLFTab, EFMTab, DBFTab, PMFTab };
