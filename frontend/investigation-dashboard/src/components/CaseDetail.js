import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, Typography, Grid, Chip, Button, TextField,
  Divider, CircularProgress, Alert, List, ListItem, ListItemText,
  Dialog, DialogTitle, DialogContent, DialogActions, Paper,
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import NoteAddIcon from '@mui/icons-material/NoteAdd';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import DescriptionIcon from '@mui/icons-material/Description';
import { getCase, getCaseNotes, addCaseNote, escalateCase, closeCase, generateSAR } from '../services/api';
import { useSnackbar } from 'notistack';

const statusColors = { open: 'info', in_progress: 'warning', escalated: 'error', closed: 'default', filed: 'success' };

export default function CaseDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();
  const [caseData, setCaseData] = useState(null);
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [dialog, setDialog] = useState({ open: false, type: '', value: '' });

  const fetchData = async () => {
    try {
      const [caseRes, notesRes] = await Promise.all([
        getCase(id),
        getCaseNotes(id).catch(() => ({ data: [] })),
      ]);
      setCaseData(caseRes.data);
      setNotes(notesRes.data?.notes || notesRes.data || []);
    } catch (err) {
      enqueueSnackbar('Failed to load case', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [id]);

  const handleAction = async () => {
    try {
      if (dialog.type === 'note') {
        await addCaseNote(id, { content: dialog.value, note_type: 'investigation' });
        enqueueSnackbar('Note added', { variant: 'success' });
      } else if (dialog.type === 'escalate') {
        await escalateCase(id, { reason: dialog.value });
        enqueueSnackbar('Case escalated', { variant: 'success' });
      } else if (dialog.type === 'close') {
        await closeCase(id, { resolution: dialog.value });
        enqueueSnackbar('Case closed', { variant: 'success' });
      } else if (dialog.type === 'sar') {
        await generateSAR(id);
        enqueueSnackbar('SAR generated', { variant: 'success' });
      }
      setDialog({ open: false, type: '', value: '' });
      fetchData();
    } catch (err) {
      enqueueSnackbar(`Action failed: ${err.response?.data?.detail || err.message}`, { variant: 'error' });
    }
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;
  if (!caseData) return <Alert severity="error">Case not found</Alert>;

  return (
    <Box>
      <Button startIcon={<ArrowBackIcon />} onClick={() => navigate('/cases')} sx={{ mb: 2 }}>
        Back to Cases
      </Button>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h5">{caseData.title || `Case ${id}`}</Typography>
                <Chip label={caseData.status?.replace(/_/g, ' ')} color={statusColors[caseData.status] || 'default'} />
              </Box>
              <Divider sx={{ mb: 2 }} />
              <Grid container spacing={2}>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Case ID</Typography>
                  <Typography>{caseData.case_id || id}</Typography></Grid>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Priority</Typography>
                  <Chip label={caseData.priority} size="small" /></Grid>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Assigned To</Typography>
                  <Typography>{caseData.assigned_to || 'Unassigned'}</Typography></Grid>
                <Grid item xs={6}><Typography variant="body2" color="text.secondary">Created</Typography>
                  <Typography>{caseData.created_at ? new Date(caseData.created_at).toLocaleString() : 'N/A'}</Typography></Grid>
                <Grid item xs={12}><Typography variant="body2" color="text.secondary">Description</Typography>
                  <Typography>{caseData.description || 'No description'}</Typography></Grid>
              </Grid>

              {caseData.alert_ids && caseData.alert_ids.length > 0 && (
                <Box sx={{ mt: 3 }}>
                  <Typography variant="subtitle1" sx={{ mb: 1 }}>Linked Alerts</Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {caseData.alert_ids.map((aid) => (
                      <Chip key={aid} label={aid} size="small" clickable
                        onClick={() => navigate(`/alerts/${aid}`)} />
                    ))}
                  </Box>
                </Box>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Investigation Notes</Typography>
              {notes.length === 0 ? (
                <Typography color="text.secondary">No notes yet</Typography>
              ) : (
                <List>
                  {notes.map((note, i) => (
                    <Paper key={i} variant="outlined" sx={{ mb: 1, p: 2 }}>
                      <ListItem disablePadding>
                        <ListItemText
                          primary={note.content}
                          secondary={`${note.created_by || 'Unknown'} - ${note.created_at ? new Date(note.created_at).toLocaleString() : ''}`}
                        />
                      </ListItem>
                    </Paper>
                  ))}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>Actions</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Button variant="outlined" startIcon={<NoteAddIcon />} fullWidth
                  onClick={() => setDialog({ open: true, type: 'note', value: '' })}>
                  Add Note
                </Button>
                <Button variant="outlined" color="warning" startIcon={<TrendingUpIcon />} fullWidth
                  onClick={() => setDialog({ open: true, type: 'escalate', value: '' })}
                  disabled={caseData.status === 'closed'}>
                  Escalate
                </Button>
                <Button variant="outlined" color="success" startIcon={<CheckCircleIcon />} fullWidth
                  onClick={() => setDialog({ open: true, type: 'close', value: '' })}
                  disabled={caseData.status === 'closed'}>
                  Close Case
                </Button>
                <Divider />
                <Button variant="contained" color="secondary" startIcon={<DescriptionIcon />} fullWidth
                  onClick={() => setDialog({ open: true, type: 'sar', value: '' })}>
                  Generate SAR
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Dialog open={dialog.open} onClose={() => setDialog({ open: false, type: '', value: '' })} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialog.type === 'note' && 'Add Investigation Note'}
          {dialog.type === 'escalate' && 'Escalate Case'}
          {dialog.type === 'close' && 'Close Case'}
          {dialog.type === 'sar' && 'Generate SAR Report'}
        </DialogTitle>
        <DialogContent>
          {dialog.type === 'sar' ? (
            <Typography>Generate a Suspicious Activity Report from this case?</Typography>
          ) : (
            <TextField
              autoFocus fullWidth margin="normal" multiline rows={4}
              label={dialog.type === 'note' ? 'Note' : 'Reason'}
              value={dialog.value}
              onChange={(e) => setDialog({ ...dialog, value: e.target.value })}
            />
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog({ open: false, type: '', value: '' })}>Cancel</Button>
          <Button variant="contained" onClick={handleAction}>
            {dialog.type === 'sar' ? 'Generate' : 'Submit'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
