import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Typography, Chip, TextField, MenuItem, Grid, Card, CardContent,
  CircularProgress, IconButton, Tooltip,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import VisibilityIcon from '@mui/icons-material/Visibility';
import { getAlerts } from '../services/api';

const severityColors = { critical: 'error', high: 'warning', medium: 'info', low: 'success' };
const statusColors = { new: 'info', open: 'warning', assigned: 'primary', escalated: 'error', closed: 'default' };

export default function AlertList() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ status: '', severity: '', type: '' });
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 25 });
  const navigate = useNavigate();

  useEffect(() => {
    const fetchAlerts = async () => {
      setLoading(true);
      try {
        const params = { limit: 100 };
        if (filters.status) params.status = filters.status;
        if (filters.severity) params.severity = filters.severity;
        if (filters.type) params.alert_type = filters.type;
        const res = await getAlerts(params);
        const data = res.data?.alerts || res.data || [];
        setAlerts(data.map((a, i) => ({ ...a, id: a.alert_id || a.id || i })));
      } catch (err) {
        console.error('Failed to fetch alerts:', err);
        setAlerts([]);
      } finally {
        setLoading(false);
      }
    };
    fetchAlerts();
  }, [filters]);

  const columns = [
    { field: 'id', headerName: 'Alert ID', width: 130 },
    { field: 'alert_type', headerName: 'Type', width: 160, renderCell: (p) => p.value?.replace(/_/g, ' ') || 'N/A' },
    {
      field: 'severity', headerName: 'Severity', width: 120,
      renderCell: (p) => <Chip label={p.value} size="small" color={severityColors[p.value] || 'default'} />,
    },
    {
      field: 'status', headerName: 'Status', width: 120,
      renderCell: (p) => <Chip label={p.value} size="small" color={statusColors[p.value] || 'default'} variant="outlined" />,
    },
    { field: 'risk_score', headerName: 'Risk Score', width: 110, type: 'number' },
    { field: 'customer_id', headerName: 'Customer', width: 140 },
    { field: 'created_at', headerName: 'Created', width: 180, valueFormatter: (params) => params.value ? new Date(params.value).toLocaleString() : '' },
    {
      field: 'actions', headerName: 'Actions', width: 80, sortable: false,
      renderCell: (p) => (
        <Tooltip title="View Details">
          <IconButton size="small" onClick={() => navigate(`/alerts/${p.row.id}`)}>
            <VisibilityIcon />
          </IconButton>
        </Tooltip>
      ),
    },
  ];

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>Alert Queue</Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField select fullWidth label="Status" size="small" value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="new">New</MenuItem>
                <MenuItem value="open">Open</MenuItem>
                <MenuItem value="assigned">Assigned</MenuItem>
                <MenuItem value="escalated">Escalated</MenuItem>
                <MenuItem value="closed">Closed</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField select fullWidth label="Severity" size="small" value={filters.severity}
                onChange={(e) => setFilters({ ...filters, severity: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="critical">Critical</MenuItem>
                <MenuItem value="high">High</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="low">Low</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField select fullWidth label="Type" size="small" value={filters.type}
                onChange={(e) => setFilters({ ...filters, type: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="aml">AML</MenuItem>
                <MenuItem value="fraud">Fraud</MenuItem>
                <MenuItem value="sanctions">Sanctions</MenuItem>
                <MenuItem value="network">Network</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <DataGrid
          rows={alerts}
          columns={columns}
          loading={loading}
          paginationModel={paginationModel}
          onPaginationModelChange={setPaginationModel}
          pageSizeOptions={[10, 25, 50]}
          autoHeight
          disableRowSelectionOnClick
          sx={{ border: 0, '& .MuiDataGrid-cell': { borderBottom: '1px solid #f0f0f0' } }}
        />
      </Card>
    </Box>
  );
}
