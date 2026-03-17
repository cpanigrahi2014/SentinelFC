import React, { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, Paper, Tabs, Tab, Grid, Card, CardContent, Chip, Button,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  CircularProgress, Alert, TextField, MenuItem,
  Divider, Accordion, AccordionSummary, AccordionDetails,
  List, ListItem, ListItemIcon, ListItemText, LinearProgress,
} from '@mui/material';
import PsychologyIcon from '@mui/icons-material/Psychology';
import DashboardIcon from '@mui/icons-material/Dashboard';
import ModelTrainingIcon from '@mui/icons-material/ModelTraining';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import PersonSearchIcon from '@mui/icons-material/PersonSearch';
import GroupWorkIcon from '@mui/icons-material/GroupWork';
import AnomalyIcon from '@mui/icons-material/BugReport';
import ScoreIcon from '@mui/icons-material/Speed';
import ExplainIcon from '@mui/icons-material/Visibility';
import GovernanceIcon from '@mui/icons-material/Policy';
import StorageIcon from '@mui/icons-material/Storage';
import TuneIcon from '@mui/icons-material/Tune';
import PlayArrowIcon from '@mui/icons-material/PlayArrow';
import InfoIcon from '@mui/icons-material/Info';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import WarningAmberIcon from '@mui/icons-material/WarningAmber';
import RefreshIcon from '@mui/icons-material/Refresh';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import {
  getAimlDashboard, getAimlModels, aimlPredictAml, aimlPredictFraud,
  aimlBehavioralUpdate, aimlPeerGroupAnalyze, aimlAnomalyDetect,
  aimlRiskPredict, aimlXaiExplain, getAimlGovernance,
  aimlIngestionRun, aimlSimulationRun,
  aimlScenarioAlertReduction, aimlScenarioPredictiveFraud,
  aimlScenarioRiskUpdate, getAimlInfo,
} from '../services/api';

// ═══════════════════ Helpers ═══════════════════

const riskColor = (r) => {
  const m = { critical: 'error', high: 'warning', medium: 'info', low: 'success' };
  return m[r] || 'default';
};

const pct = (v) => `${(v * 100).toFixed(1)}%`;

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

  const load = useCallback(async () => {
    setLoading(true);
    try { const r = await getAimlDashboard(); setData(r.data); }
    catch (e) { console.error('Failed to load AI/ML dashboard:', e); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Box display="flex" justifyContent="center" py={4}><CircularProgress /></Box>;
  if (!data) return <Alert severity="info">No dashboard data available</Alert>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6"><DashboardIcon sx={{ mr: 1, verticalAlign: 'middle' }} />AI/ML Analytics Dashboard</Typography>
        <Button startIcon={<RefreshIcon />} onClick={load}>Refresh</Button>
      </Box>
      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} sm={3}><StatCard title="Active Models" value={data.model_metrics?.active_models} color="primary.main" subtitle={`Avg accuracy: ${pct(data.model_metrics?.avg_accuracy || 0)}`} /></Grid>
        <Grid item xs={6} sm={3}><StatCard title="Total Features" value={data.model_metrics?.total_features} color="info.main" subtitle={`${(data.model_metrics?.total_training_samples / 1e6).toFixed(0)}M training samples`} /></Grid>
        <Grid item xs={6} sm={3}><StatCard title="Behavioral Profiles" value={data.behavioral_analytics?.profiles_tracked} color="success.main" subtitle={`${data.behavioral_analytics?.baselines_established} baselines`} /></Grid>
        <Grid item xs={6} sm={3}><StatCard title="Peer Groups" value={data.peer_groups?.groups_defined} color="warning.main" /></Grid>
      </Grid>
      <Grid container spacing={2} mb={3}>
        <Grid item xs={6} sm={3}><StatCard title="Anomaly Methods" value={data.anomaly_detection?.methods_available} /></Grid>
        <Grid item xs={6} sm={3}><StatCard title="XAI Methods" value={data.xai_methods?.length} /></Grid>
        <Grid item xs={6} sm={3}><StatCard title="Ingestion Jobs" value={data.ingestion_jobs?.total_completed} subtitle={`Last: ${data.ingestion_jobs?.last_job?.records_ingested?.toLocaleString()} records`} /></Grid>
        <Grid item xs={6} sm={3}><StatCard title="Simulations Run" value={data.simulations?.total_run} subtitle={`Last alert reduction: ${data.simulations?.last_simulation?.metrics?.alert_reduction_pct?.toFixed(1)}%`} /></Grid>
      </Grid>
      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>Peer Groups</Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          {data.peer_groups?.groups?.map((g) => <Chip key={g} label={g.replace(/_/g, ' ')} variant="outlined" />)}
        </Box>
        <Divider sx={{ my: 2 }} />
        <Typography variant="subtitle1" gutterBottom>Anomaly Detection Methods</Typography>
        <Box display="flex" gap={1} flexWrap="wrap">
          {data.anomaly_detection?.methods?.map((m) => <Chip key={m} label={m.replace(/_/g, ' ')} color="info" variant="outlined" />)}
        </Box>
      </Paper>
    </Box>
  );
}

// ═══════════════════ Model Registry Tab ═══════════════════

function ModelRegistryTab() {
  const [models, setModels] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try { const r = await getAimlModels(); setModels(r.data); }
    catch (e) { console.error('Failed to load models:', e); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Box display="flex" justifyContent="center" py={4}><CircularProgress /></Box>;
  if (!models) return <Alert severity="info">No model data</Alert>;

  return (
    <Box>
      <Typography variant="h6" mb={2}><ModelTrainingIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Model Registry ({models.total} models, {models.active} active)</Typography>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Model ID</TableCell><TableCell>Name</TableCell><TableCell>Type</TableCell>
              <TableCell>Framework</TableCell><TableCell>Status</TableCell><TableCell>Features</TableCell>
              <TableCell>Accuracy</TableCell><TableCell>AUC-ROC</TableCell><TableCell>FPR</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {models.models?.map((m) => (
              <TableRow key={m.model_id}>
                <TableCell><Typography variant="body2" fontWeight={600}>{m.model_id}</Typography></TableCell>
                <TableCell>{m.name}</TableCell>
                <TableCell><Chip label={m.type} size="small" variant="outlined" /></TableCell>
                <TableCell>{m.framework}</TableCell>
                <TableCell><Chip label={m.status} size="small" color="success" /></TableCell>
                <TableCell>{m.features}</TableCell>
                <TableCell>{m.accuracy ? pct(m.accuracy) : 'N/A'}</TableCell>
                <TableCell>{m.auc_roc ? m.auc_roc.toFixed(3) : 'N/A'}</TableCell>
                <TableCell>{m.false_positive_rate ? pct(m.false_positive_rate) : 'N/A'}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}

// ═══════════════════ ML Predictions Tab ═══════════════════

function PredictionsTab() {
  const [mode, setMode] = useState('aml');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [amount, setAmount] = useState(50000);

  const runAml = async () => {
    setLoading(true);
    try { const r = await aimlPredictAml({ amount, is_international: true, is_pep: false }); setResult(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  };

  const runFraud = async () => {
    setLoading(true);
    try { const r = await aimlPredictFraud({ amount, channel: 'online', hour_of_day: 3, device_trust_score: 0.3 }); setResult(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}><TrendingUpIcon sx={{ mr: 1, verticalAlign: 'middle' }} />ML Predictions</Typography>
      <Box display="flex" gap={2} mb={2} alignItems="center">
        <TextField select label="Model" value={mode} onChange={(e) => { setMode(e.target.value); setResult(null); }} size="small" sx={{ width: 200 }}>
          <MenuItem value="aml">AML Classifier</MenuItem>
          <MenuItem value="fraud">Fraud Detector</MenuItem>
        </TextField>
        <TextField label="Amount ($)" type="number" value={amount} onChange={(e) => setAmount(Number(e.target.value))} size="small" sx={{ width: 150 }} />
        <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={mode === 'aml' ? runAml : runFraud} disabled={loading}>
          {loading ? 'Running...' : 'Run Prediction'}
        </Button>
      </Box>
      {result && (
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Model</Typography><Typography fontWeight={600}>{result.model_id}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Score</Typography><Typography fontWeight={600} color={result.risk_level === 'critical' ? 'error.main' : result.risk_level === 'high' ? 'warning.main' : 'success.main'}>{(result.aml_score || result.fraud_score)?.toFixed(4)}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Risk Level</Typography><Chip label={result.risk_level} color={riskColor(result.risk_level)} size="small" /></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Confidence</Typography><Typography>{pct(result.confidence)}</Typography></Grid>
          </Grid>
          {result.explanation?.top_risk_drivers && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" gutterBottom>Risk Drivers (SHAP)</Typography>
              {result.explanation.top_risk_drivers.map((d, i) => (
                <Chip key={i} label={`${d.feature}: ${d.impact.toFixed(4)} (${d.direction})`} size="small" sx={{ mr: 1, mb: 1 }} variant="outlined"
                      color={d.direction === 'increases_risk' ? 'error' : 'default'} />
              ))}
            </>
          )}
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ Behavioral Analytics Tab ═══════════════════

function BehavioralTab() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [custId, setCustId] = useState('CUST-BEH-001');
  const [amt, setAmt] = useState(25000);

  const run = async () => {
    setLoading(true);
    try { const r = await aimlBehavioralUpdate({ customer_id: custId, amount: amt }); setResult(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}><PersonSearchIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Adaptive Behavioral Analytics</Typography>
      <Box display="flex" gap={2} mb={2} alignItems="center">
        <TextField label="Customer ID" value={custId} onChange={(e) => setCustId(e.target.value)} size="small" />
        <TextField label="Amount ($)" type="number" value={amt} onChange={(e) => setAmt(Number(e.target.value))} size="small" sx={{ width: 150 }} />
        <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={run} disabled={loading}>Update Profile</Button>
      </Box>
      {result && (
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Customer</Typography><Typography fontWeight={600}>{result.customer_id}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Observations</Typography><Typography>{result.observations}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Avg Amount</Typography><Typography>${result.avg_transaction_amount?.toLocaleString()}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Risk Adj</Typography><Chip label={result.risk_adjustment} color={result.risk_adjustment === 'elevated' ? 'warning' : 'success'} size="small" /></Grid>
          </Grid>
          {result.deviations?.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              <Typography variant="subtitle2" color="error.main" gutterBottom>Deviations Detected</Typography>
              {result.deviations.map((d, i) => (
                <Alert key={i} severity="warning" sx={{ mb: 1 }}>{d.detail} (z-score: {d.z_score})</Alert>
              ))}
            </>
          )}
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ Peer Group Analysis Tab ═══════════════════

function PeerGroupTab() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [group, setGroup] = useState('retail_banking_individual');
  const [amt, setAmt] = useState(35000);

  const run = async () => {
    setLoading(true);
    try { const r = await aimlPeerGroupAnalyze({ peer_group: group, monthly_amount: amt, customer_id: 'CUST-PGA-001' }); setResult(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}><GroupWorkIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Peer Group Analysis</Typography>
      <Box display="flex" gap={2} mb={2} alignItems="center">
        <TextField select label="Peer Group" value={group} onChange={(e) => setGroup(e.target.value)} size="small" sx={{ width: 250 }}>
          {['retail_banking_individual', 'small_business', 'corporate', 'high_net_worth', 'money_service_business'].map(g => (
            <MenuItem key={g} value={g}>{g.replace(/_/g, ' ')}</MenuItem>
          ))}
        </TextField>
        <TextField label="Monthly Amount ($)" type="number" value={amt} onChange={(e) => setAmt(Number(e.target.value))} size="small" sx={{ width: 180 }} />
        <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={run} disabled={loading}>Analyze</Button>
      </Box>
      {result && (
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Peer Group</Typography><Typography fontWeight={600}>{result.peer_group?.replace(/_/g, ' ')}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Z-Score</Typography><Typography fontWeight={600}>{result.metrics?.monthly_amount?.z_score}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Peer Avg</Typography><Typography>${result.metrics?.monthly_amount?.peer_avg?.toLocaleString()}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Risk Level</Typography><Chip label={result.risk_level} color={riskColor(result.risk_level)} size="small" /></Grid>
          </Grid>
          {result.anomaly_flags?.length > 0 && (
            <>
              <Divider sx={{ my: 2 }} />
              {result.anomaly_flags.map((f, i) => <Alert key={i} severity="error" sx={{ mb: 1 }}>{f.detail}</Alert>)}
            </>
          )}
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ Anomaly Detection Tab ═══════════════════

function AnomalyTab() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    try {
      const r = await aimlAnomalyDetect({
        transactions: [
          { transaction_id: 'TXN-A001', amount: 75000 },
          { transaction_id: 'TXN-A002', amount: 3200 },
          { transaction_id: 'TXN-A003', amount: 125000 },
          { transaction_id: 'TXN-A004', amount: 800 },
        ],
      });
      setResult(r.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}><AnomalyIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Multi-Method Anomaly Detection</Typography>
      <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={run} disabled={loading} sx={{ mb: 2 }}>
        Run Anomaly Detection (Sample Batch)
      </Button>
      {result && (
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2} mb={2}>
            <Grid item xs={3}><StatCard title="Transactions" value={result.total_transactions} /></Grid>
            <Grid item xs={3}><StatCard title="Anomalies" value={result.anomalies_detected} color="error.main" /></Grid>
            <Grid item xs={3}><StatCard title="Anomaly Rate" value={pct(result.anomaly_rate)} /></Grid>
            <Grid item xs={3}><StatCard title="Methods Used" value={result.methods_used?.length} /></Grid>
          </Grid>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell>Txn ID</TableCell><TableCell>Amount</TableCell>
                  <TableCell>Isolation Forest</TableCell><TableCell>Autoencoder</TableCell>
                  <TableCell>Z-Score</TableCell><TableCell>Ensemble</TableCell><TableCell>Anomaly?</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {result.results?.map((r) => (
                  <TableRow key={r.transaction_id} sx={r.is_anomaly ? { bgcolor: 'error.50' } : {}}>
                    <TableCell>{r.transaction_id}</TableCell>
                    <TableCell>${r.amount?.toLocaleString()}</TableCell>
                    <TableCell>{r.method_scores?.isolation_forest?.toFixed(4)}</TableCell>
                    <TableCell>{r.method_scores?.autoencoder?.toFixed(4)}</TableCell>
                    <TableCell>{r.method_scores?.statistical_zscore?.toFixed(4)}</TableCell>
                    <TableCell fontWeight={600}>{r.ensemble_score?.toFixed(4)}</TableCell>
                    <TableCell>{r.is_anomaly ? <Chip label="ANOMALY" color="error" size="small" /> : <Chip label="Normal" size="small" />}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ Risk Scoring Tab ═══════════════════

function RiskScoringTab() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [factors, setFactors] = useState({
    demographics_risk: 0.15, transaction_risk: 0.65,
    behavioral_risk: 0.55, network_risk: 0.40,
    external_risk: 0.50, kyc_risk: 0.30,
  });

  const run = async () => {
    setLoading(true);
    try { const r = await aimlRiskPredict({ customer_id: 'CUST-RSK-001', ...factors }); setResult(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}><ScoreIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Predictive Risk Scoring</Typography>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle2" gutterBottom>Risk Factor Inputs (0.0 - 1.0)</Typography>
        <Grid container spacing={2}>
          {Object.entries(factors).map(([k, v]) => (
            <Grid item xs={4} key={k}>
              <TextField label={k.replace(/_/g, ' ')} type="number" value={v} onChange={(e) => setFactors({ ...factors, [k]: Number(e.target.value) })}
                size="small" fullWidth inputProps={{ step: 0.05, min: 0, max: 1 }} />
            </Grid>
          ))}
        </Grid>
        <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={run} disabled={loading} sx={{ mt: 2 }}>
          Calculate Risk Score
        </Button>
      </Paper>
      {result && (
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Risk Score</Typography><Typography variant="h4" fontWeight={700} color={riskColor(result.risk_level) + '.main'}>{result.risk_score?.toFixed(4)}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Risk Level</Typography><Chip label={result.risk_level} color={riskColor(result.risk_level)} /></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Previous</Typography><Typography>{result.previous_score}</Typography></Grid>
            <Grid item xs={3}><Typography variant="body2" color="text.secondary">Trend</Typography><Chip label={result.trend} color={result.trend === 'increasing' ? 'warning' : 'success'} size="small" /></Grid>
          </Grid>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>Component Scores & Weights</Typography>
          {Object.entries(result.component_scores || {}).map(([k, v]) => (
            <Box key={k} display="flex" alignItems="center" gap={1} mb={0.5}>
              <Typography variant="body2" sx={{ width: 120 }}>{k}</Typography>
              <LinearProgress variant="determinate" value={v * 100} sx={{ flex: 1, height: 8, borderRadius: 4 }}
                color={v > 0.6 ? 'error' : v > 0.3 ? 'warning' : 'success'} />
              <Typography variant="body2" sx={{ width: 60 }}>{v.toFixed(2)} (x{result.weights?.[k]?.toFixed(2)})</Typography>
            </Box>
          ))}
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ XAI Tab ═══════════════════

function XAITab() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    setLoading(true);
    try {
      const r = await aimlXaiExplain({
        model_id: 'MDL-AML-001', score: 0.72,
        features: { amount: 0.7, velocity: 0.5, geographic_risk: 0.6, pep: 0.0, device_trust: 0.8 },
      });
      setResult(r.data);
    } catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}><ExplainIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Explainable AI (XAI)</Typography>
      <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={run} disabled={loading} sx={{ mb: 2 }}>
        Generate Explanation (Sample Prediction)
      </Button>
      {result && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="subtitle1" gutterBottom>Model: {result.model_id} — Score: {result.prediction_score}</Typography>
          <Divider sx={{ my: 1 }} />
          <Typography variant="subtitle2" gutterBottom>SHAP Analysis — Top Risk Drivers</Typography>
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow><TableCell>Feature</TableCell><TableCell>Value</TableCell><TableCell>SHAP Value</TableCell><TableCell>Direction</TableCell></TableRow>
              </TableHead>
              <TableBody>
                {result.shap_analysis?.top_risk_drivers?.map((d, i) => (
                  <TableRow key={i}>
                    <TableCell fontWeight={600}>{d.feature}</TableCell>
                    <TableCell>{d.value}</TableCell>
                    <TableCell>{d.shap_value?.toFixed(4)}</TableCell>
                    <TableCell><Chip label={d.direction?.replace(/_/g, ' ')} size="small" color={d.direction === 'increases_risk' ? 'error' : 'success'} /></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
          <Divider sx={{ my: 2 }} />
          <Typography variant="subtitle2" gutterBottom>Counterfactual Analysis</Typography>
          {Object.entries(result.counterfactual_analysis?.changes || {}).map(([k, v]) => (
            <Chip key={k} sx={{ mr: 1, mb: 1 }} variant="outlined"
              label={`${k}: ${v.current} → ${v.counterfactual} ${v.would_change_prediction ? '(would change)' : ''}`}
              color={v.would_change_prediction ? 'warning' : 'default'} />
          ))}
          <Divider sx={{ my: 2 }} />
          <Alert severity="info">{result.human_readable_summary}</Alert>
          <Box mt={2} display="flex" gap={1} flexWrap="wrap">
            <Typography variant="body2" color="text.secondary">Available XAI methods:</Typography>
            {result.xai_methods?.map(m => <Chip key={m} label={m.replace(/_/g, ' ')} size="small" variant="outlined" />)}
          </Box>
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ Governance Tab ═══════════════════

function GovernanceTab() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try { const r = await getAimlGovernance(); setData(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Box display="flex" justifyContent="center" py={4}><CircularProgress /></Box>;
  if (!data) return <Alert severity="info">No governance data</Alert>;

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6"><GovernanceIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Model Governance & Monitoring</Typography>
        <Button startIcon={<RefreshIcon />} onClick={load}>Refresh</Button>
      </Box>
      <Grid container spacing={2} mb={3}>
        <Grid item xs={3}><StatCard title="Total Models" value={data.total_models} /></Grid>
        <Grid item xs={3}><StatCard title="Drift Alerts" value={data.drift_alerts} color="warning.main" /></Grid>
        <Grid item xs={3}><StatCard title="Retraining Needed" value={data.retraining_needed} color="error.main" /></Grid>
        <Grid item xs={3}><StatCard title="Active" value={data.active_models} color="success.main" /></Grid>
      </Grid>
      <TableContainer component={Paper}>
        <Table size="small">
          <TableHead>
            <TableRow>
              <TableCell>Model</TableCell><TableCell>Status</TableCell><TableCell>Accuracy</TableCell>
              <TableCell>PSI</TableCell><TableCell>Drift</TableCell><TableCell>Retrain?</TableCell>
              <TableCell>Compliance</TableCell><TableCell>Tier</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {data.models?.map((m) => (
              <TableRow key={m.model_id}>
                <TableCell><Typography variant="body2" fontWeight={600}>{m.model_id}</Typography><Typography variant="caption">{m.model_name}</Typography></TableCell>
                <TableCell><Chip label={m.status} size="small" color="success" /></TableCell>
                <TableCell>{m.accuracy ? pct(m.accuracy) : 'N/A'}</TableCell>
                <TableCell>{m.population_stability_index?.toFixed(2)}</TableCell>
                <TableCell>{m.data_drift_detected ? <WarningAmberIcon color="warning" fontSize="small" /> : <CheckCircleIcon color="success" fontSize="small" />}</TableCell>
                <TableCell>{m.retraining_recommended ? <ErrorIcon color="error" fontSize="small" /> : <CheckCircleIcon color="success" fontSize="small" />}</TableCell>
                <TableCell><Chip label={m.compliance_status} size="small" color="success" /></TableCell>
                <TableCell><Chip label={m.model_risk_tier} size="small" variant="outlined" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <Paper sx={{ p: 2, mt: 2 }}>
        <Typography variant="subtitle2" gutterBottom>Governance Policies</Typography>
        <Grid container spacing={2}>
          <Grid item xs={3}><Typography variant="body2" color="text.secondary">Max PSI</Typography><Typography>{data.governance_policies?.max_psi_threshold}</Typography></Grid>
          <Grid item xs={3}><Typography variant="body2" color="text.secondary">Min Accuracy</Typography><Typography>{data.governance_policies?.min_accuracy_threshold}</Typography></Grid>
          <Grid item xs={3}><Typography variant="body2" color="text.secondary">Retrain Freq</Typography><Typography>{data.governance_policies?.retraining_frequency}</Typography></Grid>
          <Grid item xs={3}><Typography variant="body2" color="text.secondary">Validation Freq</Typography><Typography>{data.governance_policies?.validation_frequency}</Typography></Grid>
        </Grid>
      </Paper>
    </Box>
  );
}

// ═══════════════════ Data Ingestion Tab ═══════════════════

function IngestionTab() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [records, setRecords] = useState(100000);
  const [source, setSource] = useState('transaction_feed');

  const run = async () => {
    setLoading(true);
    try { const r = await aimlIngestionRun({ record_count: records, source_type: source }); setResult(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}><StorageIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Data Ingestion & Big Data Analytics</Typography>
      <Box display="flex" gap={2} mb={2} alignItems="center">
        <TextField select label="Source Type" value={source} onChange={(e) => setSource(e.target.value)} size="small" sx={{ width: 200 }}>
          {['transaction_feed', 'customer_data', 'watchlist', 'market_data', 'external_api'].map(s => (
            <MenuItem key={s} value={s}>{s.replace(/_/g, ' ')}</MenuItem>
          ))}
        </TextField>
        <TextField label="Record Count" type="number" value={records} onChange={(e) => setRecords(Number(e.target.value))} size="small" sx={{ width: 150 }} />
        <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={run} disabled={loading}>Run Ingestion</Button>
      </Box>
      {result && (
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2} mb={2}>
            <Grid item xs={3}><StatCard title="Records Ingested" value={result.records_ingested?.toLocaleString()} /></Grid>
            <Grid item xs={3}><StatCard title="Anomalies Flagged" value={result.anomalies_flagged?.toLocaleString()} color="warning.main" /></Grid>
            <Grid item xs={3}><StatCard title="Processing Time" value={`${result.processing_time_seconds}s`} /></Grid>
            <Grid item xs={3}><StatCard title="Data Quality" value={pct(result.data_quality_score)} color="success.main" /></Grid>
          </Grid>
          <Typography variant="subtitle2" gutterBottom>Pipeline Stages</Typography>
          {result.pipeline_stages?.map((s) => (
            <Box key={s.stage} display="flex" alignItems="center" gap={1} mb={0.5}>
              <CheckCircleIcon color="success" fontSize="small" />
              <Typography variant="body2" sx={{ width: 140 }}>{s.stage}</Typography>
              <LinearProgress variant="determinate" value={100} sx={{ flex: 1, height: 6, borderRadius: 3 }} color="success" />
              <Typography variant="caption">{s.duration_sec}s</Typography>
            </Box>
          ))}
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ Simulation Tab ═══════════════════

function SimulationTab() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [threshold, setThreshold] = useState(0.6);

  const run = async () => {
    setLoading(true);
    try { const r = await aimlSimulationRun({ model_id: 'MDL-AML-001', threshold, dataset_size: 50000 }); setResult(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}><TuneIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Scenario Simulation & Tuning</Typography>
      <Box display="flex" gap={2} mb={2} alignItems="center">
        <TextField label="Threshold" type="number" value={threshold} onChange={(e) => setThreshold(Number(e.target.value))}
          size="small" sx={{ width: 150 }} inputProps={{ step: 0.05, min: 0.1, max: 0.95 }} />
        <Button variant="contained" startIcon={<PlayArrowIcon />} onClick={run} disabled={loading}>Run Simulation</Button>
      </Box>
      {result && (
        <Paper sx={{ p: 2 }}>
          <Grid container spacing={2} mb={2}>
            <Grid item xs={3}><StatCard title="Precision" value={pct(result.metrics?.precision)} /></Grid>
            <Grid item xs={3}><StatCard title="Recall" value={pct(result.metrics?.recall)} /></Grid>
            <Grid item xs={3}><StatCard title="F1 Score" value={pct(result.metrics?.f1_score)} /></Grid>
            <Grid item xs={3}><StatCard title="Alert Reduction" value={`${result.metrics?.alert_reduction_pct?.toFixed(1)}%`} color="success.main" /></Grid>
          </Grid>
          <Typography variant="subtitle2" gutterBottom>Confusion Matrix</Typography>
          <Grid container spacing={1} mb={2}>
            <Grid item xs={3}><Chip label={`TP: ${result.confusion_matrix?.true_positives?.toLocaleString()}`} color="success" /></Grid>
            <Grid item xs={3}><Chip label={`FP: ${result.confusion_matrix?.false_positives?.toLocaleString()}`} color="warning" /></Grid>
            <Grid item xs={3}><Chip label={`FN: ${result.confusion_matrix?.false_negatives?.toLocaleString()}`} color="error" /></Grid>
            <Grid item xs={3}><Chip label={`TN: ${result.confusion_matrix?.true_negatives?.toLocaleString()}`} color="info" /></Grid>
          </Grid>
          <Alert severity={result.recommendation === 'optimal' ? 'success' : 'info'}>
            Recommendation: <strong>{result.recommendation?.replace(/_/g, ' ')}</strong>
          </Alert>
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ Scenarios Tab ═══════════════════

function ScenariosTab() {
  const [activeScenario, setActiveScenario] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const runScenario = async (name, fn) => {
    setActiveScenario(name); setLoading(true); setResult(null);
    try { const r = await fn(); setResult(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  };

  return (
    <Box>
      <Typography variant="h6" mb={2}><PlayArrowIcon sx={{ mr: 1, verticalAlign: 'middle' }} />Scenario Execution</Typography>
      <Grid container spacing={2} mb={3}>
        <Grid item xs={4}>
          <Card sx={{ cursor: 'pointer', border: activeScenario === 'alert' ? 2 : 0, borderColor: 'primary.main' }}
            onClick={() => runScenario('alert', aimlScenarioAlertReduction)}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600}>ML-based Alert Reduction</Typography>
              <Typography variant="body2" color="text.secondary">Reduce false positives by 40-60% while maintaining 97% recall</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={4}>
          <Card sx={{ cursor: 'pointer', border: activeScenario === 'fraud' ? 2 : 0, borderColor: 'primary.main' }}
            onClick={() => runScenario('fraud', aimlScenarioPredictiveFraud)}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600}>Predictive Fraud Detection</Typography>
              <Typography variant="body2" color="text.secondary">Pre-transaction risk scoring to prevent fraud before it occurs</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={4}>
          <Card sx={{ cursor: 'pointer', border: activeScenario === 'risk' ? 2 : 0, borderColor: 'primary.main' }}
            onClick={() => runScenario('risk', aimlScenarioRiskUpdate)}>
            <CardContent>
              <Typography variant="subtitle1" fontWeight={600}>Customer Risk Score Update</Typography>
              <Typography variant="body2" color="text.secondary">ML model recalculates risk dynamically on new data ingestion</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
      {loading && <Box display="flex" justifyContent="center" py={3}><CircularProgress /></Box>}
      {result && (
        <Paper sx={{ p: 2 }}>
          <Typography variant="h6" gutterBottom>{result.scenario}</Typography>
          {result.reduction_pct != null && (
            <Alert severity="success" sx={{ mb: 2 }}>
              False positive reduction: <strong>{result.reduction_pct}%</strong> — Target met: {result.reduction_target_met ? 'YES' : 'NO'}
            </Alert>
          )}
          {result.fraud_prevented != null && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Fraud prevented: <strong>${result.estimated_loss_prevented?.toLocaleString()}</strong> — Pre-txn score: {result.pre_transaction_score}
            </Alert>
          )}
          {result.delta != null && (
            <Alert severity="warning" sx={{ mb: 2 }}>
              Risk score: {result.previous_score} → {result.new_score} (delta +{result.delta}) — {result.previous_risk_level} → {result.new_risk_level}
            </Alert>
          )}
          <Typography variant="subtitle2" gutterBottom>Execution Steps</Typography>
          {result.steps?.map((s) => (
            <Accordion key={s.step} defaultExpanded={false}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Box display="flex" alignItems="center" gap={1}>
                  <CheckCircleIcon color="success" fontSize="small" />
                  <Typography variant="body2" fontWeight={600}>Step {s.step}: {s.action?.replace(/_/g, ' ')}</Typography>
                </Box>
              </AccordionSummary>
              <AccordionDetails><Typography variant="body2">{s.result}</Typography></AccordionDetails>
            </Accordion>
          ))}
          {result.models_used && (
            <Box mt={2} display="flex" gap={1} flexWrap="wrap">
              <Typography variant="body2" color="text.secondary">Models used:</Typography>
              {result.models_used.map(m => <Chip key={m} label={m} size="small" variant="outlined" />)}
            </Box>
          )}
        </Paper>
      )}
    </Box>
  );
}

// ═══════════════════ Info Tab ═══════════════════

function InfoTab() {
  const [info, setInfo] = useState(null);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try { const r = await getAimlInfo(); setInfo(r.data); }
    catch (e) { console.error(e); }
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  if (loading) return <Box display="flex" justifyContent="center" py={4}><CircularProgress /></Box>;
  if (!info) return <Alert severity="info">No info available</Alert>;

  return (
    <Box>
      <Typography variant="h6" mb={2}><InfoIcon sx={{ mr: 1, verticalAlign: 'middle' }} />{info.engine} v{info.version}</Typography>
      <Grid container spacing={2} mb={3}>
        <Grid item xs={3}><StatCard title="Components" value={info.total_components} /></Grid>
        <Grid item xs={3}><StatCard title="Models" value={info.model_count} /></Grid>
        <Grid item xs={3}><StatCard title="Peer Groups" value={info.peer_groups} /></Grid>
        <Grid item xs={3}><StatCard title="XAI Methods" value={info.xai_methods} /></Grid>
      </Grid>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Typography variant="subtitle1" gutterBottom>Components</Typography>
        <List dense>
          {info.components?.map((c) => (
            <ListItem key={c.name}>
              <ListItemIcon><CheckCircleIcon color="success" /></ListItemIcon>
              <ListItemText primary={c.name} secondary={c.description} />
              <Chip label={c.status} size="small" color="success" />
            </ListItem>
          ))}
        </List>
      </Paper>
      <Paper sx={{ p: 2 }}>
        <Typography variant="subtitle1" gutterBottom>Scenarios</Typography>
        <List dense>
          {info.scenarios?.map((s, i) => (
            <ListItem key={i}>
              <ListItemIcon><PlayArrowIcon color="primary" /></ListItemIcon>
              <ListItemText primary={s} />
            </ListItem>
          ))}
        </List>
      </Paper>
    </Box>
  );
}

// ═══════════════════ Main AIMLPage ═══════════════════

const TAB_CONFIG = [
  { label: 'Dashboard', icon: <DashboardIcon /> },
  { label: 'Models', icon: <ModelTrainingIcon /> },
  { label: 'Predictions', icon: <TrendingUpIcon /> },
  { label: 'Behavioral', icon: <PersonSearchIcon /> },
  { label: 'Peer Groups', icon: <GroupWorkIcon /> },
  { label: 'Anomaly', icon: <AnomalyIcon /> },
  { label: 'Risk Score', icon: <ScoreIcon /> },
  { label: 'XAI', icon: <ExplainIcon /> },
  { label: 'Governance', icon: <GovernanceIcon /> },
  { label: 'Ingestion', icon: <StorageIcon /> },
  { label: 'Simulation', icon: <TuneIcon /> },
  { label: 'Scenarios', icon: <PlayArrowIcon /> },
  { label: 'Info', icon: <InfoIcon /> },
];

export default function AIMLPage() {
  const [tab, setTab] = useState(0);

  const renderTab = () => {
    switch (tab) {
      case 0: return <DashboardTab />;
      case 1: return <ModelRegistryTab />;
      case 2: return <PredictionsTab />;
      case 3: return <BehavioralTab />;
      case 4: return <PeerGroupTab />;
      case 5: return <AnomalyTab />;
      case 6: return <RiskScoringTab />;
      case 7: return <XAITab />;
      case 8: return <GovernanceTab />;
      case 9: return <IngestionTab />;
      case 10: return <SimulationTab />;
      case 11: return <ScenariosTab />;
      case 12: return <InfoTab />;
      default: return <DashboardTab />;
    }
  };

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1} mb={2}>
        <PsychologyIcon color="primary" fontSize="large" />
        <Typography variant="h5" fontWeight={700}>AI/ML, Analytics & Risk Scoring</Typography>
      </Box>
      <Paper sx={{ mb: 2 }}>
        <Tabs value={tab} onChange={(_, v) => setTab(v)} variant="scrollable" scrollButtons="auto">
          {TAB_CONFIG.map((t, i) => <Tab key={i} label={t.label} icon={t.icon} iconPosition="start" />)}
        </Tabs>
      </Paper>
      {renderTab()}
    </Box>
  );
}
