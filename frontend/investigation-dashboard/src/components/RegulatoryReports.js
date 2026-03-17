import React, { useState, useEffect } from 'react';
import {
  Box, Card, CardContent, Typography, Tabs, Tab, Chip, CircularProgress,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper,
  Button, IconButton, Tooltip,
} from '@mui/material';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import SendIcon from '@mui/icons-material/Send';
import { getSARReports, getCTRReports, submitSAR, approveSAR, fileSAR } from '../services/api';
import { useSnackbar } from 'notistack';

function TabPanel({ children, value, index }) {
  return value === index ? <Box sx={{ pt: 2 }}>{children}</Box> : null;
}

const sarStatusColors = {
  draft: 'default', pending_review: 'warning', approved: 'info', filed: 'success', rejected: 'error',
};

export default function RegulatoryReports() {
  const [tab, setTab] = useState(0);
  const [sars, setSars] = useState([]);
  const [ctrs, setCtrs] = useState([]);
  const [loading, setLoading] = useState(true);
  const { enqueueSnackbar } = useSnackbar();

  const fetchData = async () => {
    try {
      const [sarRes, ctrRes] = await Promise.all([
        getSARReports({}).catch(() => ({ data: [] })),
        getCTRReports({}).catch(() => ({ data: [] })),
      ]);
      setSars(sarRes.data?.reports || sarRes.data || []);
      setCtrs(ctrRes.data?.reports || ctrRes.data || []);
    } catch (err) {
      enqueueSnackbar('Failed to load reports', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

  const handleSARAction = async (id, action) => {
    try {
      if (action === 'submit') await submitSAR(id);
      else if (action === 'approve') await approveSAR(id);
      else if (action === 'file') await fileSAR(id);
      enqueueSnackbar(`SAR ${action}ed successfully`, { variant: 'success' });
      fetchData();
    } catch (err) {
      enqueueSnackbar(`Failed to ${action} SAR`, { variant: 'error' });
    }
  };

  if (loading) return <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}><CircularProgress /></Box>;

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>Regulatory Reports</Typography>

      <Card>
        <CardContent>
          <Tabs value={tab} onChange={(_, v) => setTab(v)}>
            <Tab label={`SAR Reports (${sars.length})`} />
            <Tab label={`CTR Reports (${ctrs.length})`} />
          </Tabs>

          <TabPanel value={tab} index={0}>
            {sars.length === 0 ? (
              <Typography color="text.secondary">No SAR reports. Generate from Case Management.</Typography>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Report ID</TableCell>
                      <TableCell>Case ID</TableCell>
                      <TableCell>Subject</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Filing Date</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {sars.map((sar, i) => (
                      <TableRow key={i}>
                        <TableCell>{sar.report_id || sar.id || i}</TableCell>
                        <TableCell>{sar.case_id || 'N/A'}</TableCell>
                        <TableCell>{sar.subject_name || sar.customer_name || 'N/A'}</TableCell>
                        <TableCell>
                          <Chip label={sar.status?.replace(/_/g, ' ')} size="small"
                            color={sarStatusColors[sar.status] || 'default'} />
                        </TableCell>
                        <TableCell>{sar.filing_date ? new Date(sar.filing_date).toLocaleDateString() : 'Pending'}</TableCell>
                        <TableCell>
                          {sar.status === 'draft' && (
                            <Tooltip title="Submit for Review">
                              <IconButton size="small" onClick={() => handleSARAction(sar.report_id || sar.id, 'submit')}>
                                <SendIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          {sar.status === 'pending_review' && (
                            <Tooltip title="Approve">
                              <IconButton size="small" color="success"
                                onClick={() => handleSARAction(sar.report_id || sar.id, 'approve')}>
                                <CheckCircleIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          )}
                          {sar.status === 'approved' && (
                            <Button size="small" variant="outlined" color="primary"
                              onClick={() => handleSARAction(sar.report_id || sar.id, 'file')}>
                              File with FinCEN
                            </Button>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </TabPanel>

          <TabPanel value={tab} index={1}>
            {ctrs.length === 0 ? (
              <Typography color="text.secondary">No CTR reports generated</Typography>
            ) : (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Report ID</TableCell>
                      <TableCell>Customer</TableCell>
                      <TableCell>Amount</TableCell>
                      <TableCell>Transaction Date</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {ctrs.map((ctr, i) => (
                      <TableRow key={i}>
                        <TableCell>{ctr.report_id || ctr.id || i}</TableCell>
                        <TableCell>{ctr.customer_name || 'N/A'}</TableCell>
                        <TableCell>${(ctr.amount || 0).toLocaleString()}</TableCell>
                        <TableCell>{ctr.transaction_date ? new Date(ctr.transaction_date).toLocaleDateString() : 'N/A'}</TableCell>
                        <TableCell><Chip label={ctr.status || 'filed'} size="small" color="success" /></TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </TabPanel>
        </CardContent>
      </Card>
    </Box>
  );
}
