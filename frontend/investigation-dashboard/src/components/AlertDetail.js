import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Grid, Chip, Button, TextField,
  Divider, CircularProgress, Dialog, DialogTitle, DialogContent,
  DialogActions, Alert,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import PersonAddIcon from '@mui/icons-material/PersonAdd';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import FolderOpenIcon from '@mui/icons-material/FolderOpen';
import { getAlert, assignAlert, escalateAlert, closeAlert, createCase } from '../services/api';
import { useSnackbar } from 'notistack';

const severityColors = { critical: 'error', high: 'warning', medium: 'info', low: 'success' };

export default function AlertDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(true);
  const [dialog, setDialog] = useState({ open: false, type: '', value: '' });

  const fetchAlert = async () => {
    try {
      const res = await getAlert(id);
      setAlert(res.data);
    } catch (err) {
      enqueueSnackbar('Failed to load alert', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAlert(); }, [id]);

  const handleAction = async () => {
    try {
      if (dialog.type === 'assign') {
        await assignAlert(id, dialog.value);
        enqueueSnackbar('Alert assigned', { variant: 'success' });
      } else if (dialog.type === 'escalate') {
        await escalateAlert(id, dialog.value);
        enqueueSnackbar('Alert escalated', { variant: 'success' });
      } else if (dialog.type === 'close') {
        await closeAlert(id, dialog.value);
        enqueueSnackbar('Alert closed', { variant: 'success' });
      } else if (dialog.type === 'create_case') {
        await createCase({
          title: `Case from Alert ${id}`,
          description: dialog.value || `Investigation case created from alert ${id}`,
          alert_ids: [id],
          priority: alert?.severity || 'medium',
        });
        enqueueSnackbar('Case created', { variant: 'success' });
      }
      setDialog({ open: false, type: '', value: '' });
      fetchAlert();
    } catch (err) {
      enqueueSnackbar(`Action failed: ${err.response?.data?.detail || err.message}`, { variant: 'error' });
    }
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  if (!alert) return <Alert severity="error">Alert not found</Alert>;

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/alerts')} sx={{ mb: 2 }}>
        Back to Alerts
      </Button>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5">Alert {alert.alert_id || id}</Typography>
                <Chip label={alert.severity} color={severityColors[alert.severity] || 'default'} />
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Type</Typography>
                  <Typography>{alert.alert_type?.replace(/_/g, ' ') || 'N/A'}</Typography></Grid>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Status</Typography>
                  <Chip label={alert.status} size="small" variant="outlined" /></Grid>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Risk Score</Typography>
                  <Typography variant="h6" color={alert.risk_score >= 80 ? 'error' : 'text.primary'}>{alert.risk_score}</Typography></Grid>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Customer ID</Typography>
                  <Typography>{alert.customer_id || 'N/A'}</Typography></Grid>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Created</Typography>
                  <Typography>{alert.created_at ? new Date(alert.created_at).toLocaleString() : 'N/A'}</Typography></Grid>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Assigned To</Typography>
                  <Typography>{alert.assigned_to || 'Unassigned'}</Typography></Grid>
                <Grid item xs={12}><Typography variant="body2" color="text.secondary">Description</Typography>
                  <Typography>{alert.description || 'No description available'}</Typography></Grid>
              </Grid>

              {alert.triggered_rules && alert.triggered_rules.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" sx={{ mb: 1 }}>Triggered Rules</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                    {alert.triggered_rules.map((rule, i) => (
                      <Chip key={i} label={typeof rule === 'string' ? rule : rule.name || rule.rule_id} size="small" variant="outlined" />
                    ))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Actions</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Button variant="outlined" startIcon={<PersonAddIcon />} fullWidth
                  onClick={() => setDialog({ open: true, type: 'assign', value: '' })}
                  disabled={alert.status === 'closed'}>
                  Assign
                </Button>
                <Button variant="outlined" color="warning" startIcon={<TrendingUpIcon />} fullWidth
                  onClick={() => setDialog({ open: true, type: 'escalate', value: '' })}
                  disabled={alert.status === 'closed'}>
                  Escalate
                </Button>
                <Button variant="outlined" color="success" startIcon={<CheckCircleIcon />} fullWidth
                  onClick={() => setDialog({ open: true, type: 'close', value: '' })}
                  disabled={alert.status === 'closed'}>
                  Close
                </Button>
                <Divider />
                <Button variant="contained" startIcon={<FolderOpenIcon />} fullWidth
                  onClick={() => setDialog({ open: true, type: 'create_case', value: '' })}>
                  Create Case
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={dialog.open} onClose={() => setDialog({ open: false, type: '', value: '' })} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog.type === 'assign' && 'Assign Alert'}
          {dialog.type === 'escalate' && 'Escalate Alert'}
          {dialog.type === 'close' && 'Close Alert'}
          {dialog.type === 'create_case' && 'Create Investigation Case'}
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus fullWidth margin="normal"
            label={dialog.type === 'assign' ? 'Analyst ID' : dialog.type === 'create_case' ? 'Case Description' : 'Reason'}
            multiline={dialog.type !== 'assign'} rows={dialog.type !== 'assign' ? 3 : 1}
            value={dialog.value}
            onChange={(e) => setDialog({ ...dialog, value: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog({ open: false, type: '', value: '' })}>Cancel</Button>
          <Button variant="contained" onClick={handleAction}>Confirm</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
