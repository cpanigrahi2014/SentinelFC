import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, TextField, Grid, Chip,
  CircularProgress, MenuItem,
} from '@mui/material';
import { DataGrid } from '@mui/x-data-grid';
import { getAuditLogs } from '../services/api';

export default function AuditLogs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ action: '', service: '', user_id: '' });
  const [paginationModel, setPaginationModel] = useState({ page: 0, pageSize: 25 });

  useEffect(() => {
    const fetchLogs = async () => {
      setLoading(true);
      try {
        const params = { limit: 200 };
        if (filters.action) params.action = filters.action;
        if (filters.service) params.service = filters.service;
        if (filters.user_id) params.user_id = filters.user_id;
        const res = await getAuditLogs(params);
        const data = res.data?.logs || res.data || [];
        setLogs(data.map((l, i) => ({ ...l, id: l.event_id || l.id || i })));
      } catch (err) {
        setLogs([]);
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, [filters]);

  const columns = [
    { field: 'timestamp', headerName: 'Timestamp', width: 180, valueFormatter: (p) => p.value ? new Date(p.value).toLocaleString() : '' },
    { field: 'user_id', headerName: 'User', width: 130 },
    {
      field: 'action', headerName: 'Action', width: 150,
      renderCell: (p) => <Chip label={p.value} size="small" variant="outlined" />,
    },
    { field: 'resource_type', headerName: 'Resource', width: 130 },
    { field: 'resource_id', headerName: 'Resource ID', width: 160 },
    { field: 'service', headerName: 'Service', width: 150 },
    { field: 'ip_address', headerName: 'IP Address', width: 140 },
    { field: 'details', headerName: 'Details', width: 300, valueFormatter: (p) => typeof p.value === 'object' ? JSON.stringify(p.value) : p.value || '' },
  ];

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>Audit Logs</Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2}>
            <Grid item xs={12} sm={4}>
              <TextField select fullWidth label="Action" size="small" value={filters.action}
                onChange={(e) => setFilters({ ...filters, action: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="login">Login</MenuItem>
                <MenuItem value="view">View</MenuItem>
                <MenuItem value="create">Create</MenuItem>
                <MenuItem value="update">Update</MenuItem>
                <MenuItem value="delete">Delete</MenuItem>
                <MenuItem value="assign">Assign</MenuItem>
                <MenuItem value="escalate">Escalate</MenuItem>
                <MenuItem value="close">Close</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField select fullWidth label="Service" size="small" value={filters.service}
                onChange={(e) => setFilters({ ...filters, service: e.target.value })}>
                <MenuItem value="">All</MenuItem>
                <MenuItem value="api-gateway">API Gateway</MenuItem>
                <MenuItem value="alert-management">Alert Management</MenuItem>
                <MenuItem value="case-management">Case Management</MenuItem>
                <MenuItem value="transaction-monitoring">Transaction Monitoring</MenuItem>
                <MenuItem value="fraud-detection">Fraud Detection</MenuItem>
                <MenuItem value="sanctions-screening">Sanctions Screening</MenuItem>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={4}>
              <TextField fullWidth label="User ID" size="small" value={filters.user_id}
                onChange={(e) => setFilters({ ...filters, user_id: e.target.value })} />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      <Card>
        <DataGrid
          rows={logs} columns={columns} loading={loading}
          paginationModel={paginationModel} onPaginationModelChange={setPaginationModel}
          pageSizeOptions={[10, 25, 50, 100]} autoHeight disableRowSelectionOnClick
          sx={{ border: 0 }}
        />
      </Card>
    </Box>
  );
}
