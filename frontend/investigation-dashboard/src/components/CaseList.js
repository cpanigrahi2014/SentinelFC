import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Card, CardContent, Chip, Button, Grid, TextField, MenuItem,
  Dialog, DialogTitle, DialogContent, DialogActions, CircularProgress, IconButton, Tooltip,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import AddIcon from '@mui/icons-material/Add';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { getCases, createCase } from '../services/api';
import { useSnackbar } from 'notistack';

const statusColors = { open: 'info', in_progress: 'warning', escalated: 'error', closed: 'default', filed: 'success' };
const priorityColors = { critical: 'error', high: 'warning', medium: 'info', low: 'success' };

export default function CaseList() {
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: '', priority: '' });
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 25 });
  const [createDialog, setCreateDialog] = useState(false);
  const [newCase, setNewCase] = useState({ title: '', description: '', priority: 'medium' });
  const navigate = useNavigate();
  const { enqueueSnackbar } = useSnackbar();

  const fetchCases = async () => {
    setLoading(true);
    try {
      const params = { limit: 100 };
      if (filters.status) params.status = filters.status;
      if (filters.priority) params.priority = filters.priority;
      const res = await getCases(params);
      const data = res.data?.cases || res.data || [];
      setCases(data.map((c, i) => ({ ...c, id: c.case_id || c.id || i })));
    } catch (err) {
      setCases([]);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchCases(); }, [filters]);

  const handleCreate = async () => {
    try {
      await createCase(newCase);
      enqueueSnackbar('Case created', { variant: 'success' });
      setCreateDialog(false);
      setNewCase({ title: '', description: '', priority: 'medium' });
      fetchCases();
    } catch (err) {
      enqueueSnackbar('Failed to create case', { variant: 'error' });
    }
  };

  const columns = [
    { field: 'id', headerName: 'Case ID', width: 130 },
    { field: 'title', headerName: 'Title', width: 250 },
    {
      field: 'status', headerName: 'Status', width: 130,
      renderCell: (p) => <Chip label={p.value?.replace(/_/g, ' ')} size="small" color={statusColors[p.value] || 'default'} variant="outlined" />,
    },
    {
      field: 'priority', headerName: 'Priority', width: 120,
      renderCell: (p) => <Chip label={p.value} size="small" color={priorityColors[p.value] || 'default'} />,
    },
    { field: 'assigned_to', headerName: 'Assigned To', width: 150, valueFormatter: (p) => p.value || 'Unassigned' },
    { field: 'created_at', headerName: 'Created', width: 180, valueFormatter: (p) => p.value ? new Date(p.value).toLocaleString() : '' },
    {
      field: 'actions', headerName: '', width: 80, sortable: false,
      renderCell: (p) => (
        <Tooltip title="View Case">
          <IconButton size="small" onClick={() => navigate(`/cases/${p.row.id}`)}>
            <VisibilityIcon />
          </IconButton>
        </Tooltip>
      ),
    },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5">Case Management</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => setCreateDialog(true)}>
          New Case
        </Button>
      </Box>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6}>
              <TextField select fullWidth label="Status" size="small" value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="open">Open</MenuItem>
                <MenuItem value="in_progress">In Progress</MenuItem>
                <MenuItem value="escalated">Escalated</MenuItem>
                <MenuItem value="closed">Closed</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField select fullWidth label="Priority" size="small" value={filters.priority}
                onChange={(e) => setFilters({ ...filters, priority: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <DataGrid
          rows={cases} columns={columns} loading={loading}
          paginationModel={paginationModel} onPaginationModelChange={setPaginationModel}
          pageSizeOptions={[10, 25, 50]} autoHeight disableRowSelectionOnClick
          sx={{ border: 0 }}
        />
      </Card>

      <Dialog open={createDialog} onClose={() => setCreateDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Case</DialogTitle>
        <DialogContent>
          <TextField fullWidth margin="normal" label="Title" required
            value={newCase.title} onChange={(e) => setNewCase({ ...newCase, title: e.target.value })} />
          <TextField fullWidth margin="normal" label="Description" multiline rows={4}
            value={newCase.description} onChange={(e) => setNewCase({ ...newCase, description: e.target.value })} />
          <TextField select fullWidth margin="normal" label="Priority"
            value={newCase.priority} onChange={(e) => setNewCase({ ...newCase, priority: e.target.value })}>
            <MenuItem value="critical">Critical</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="low">Low</MenuItem>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleCreate} disabled={!newCase.title}>Create</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
