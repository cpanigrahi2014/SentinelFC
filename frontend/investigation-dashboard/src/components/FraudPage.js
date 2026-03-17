import React, { useState } from 'react';
import { Box, Typography, Paper, Tabs, Tab } from '@mui/material';
import ShieldIcon from '@mui/icons-material/Shield';
import TravelExploreIcon from '@mui/icons-material/TravelExplore';
import PhonelinkLockIcon from '@mui/icons-material/PhonelinkLock';
import PaymentIcon from '@mui/icons-material/Payment';
import { EFMTab, DBFTab, PMFTab } from './DataSources';

export default function FraudPage() {
  const [subTab, setSubTab] = useState(0);
  const [efmData, setEfmData] = useState(null);
  const [efmLoading, setEfmLoading] = useState(false);
  const [dbfData, setDbfData] = useState(null);
  const [dbfLoading, setDbfLoading] = useState(false);
  const [pmfData, setPmfData] = useState(null);
  const [pmfLoading, setPmfLoading] = useState(false);

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1.5} mb={2}>
        <ShieldIcon sx={{ fontSize: 32, color: 'warning.main' }} />
        <Box>
          <Typography variant="h5" fontWeight={700}>Fraud Management</Typography>
          <Typography variant="body2" color="text.secondary">
            Enterprise Fraud, Digital Banking Fraud &amp; Payments Fraud detection engines
          </Typography>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={subTab} onChange={(_, v) => setSubTab(v)} variant="scrollable" scrollButtons="auto"
          sx={{ '& .MuiTab-root': { fontWeight: 600 } }}>
          <Tab icon={<TravelExploreIcon />} iconPosition="start" label="Enterprise Fraud (EFM)" />
          <Tab icon={<PhonelinkLockIcon />} iconPosition="start" label="Digital Banking Fraud (DBF)" />
          <Tab icon={<PaymentIcon />} iconPosition="start" label="Payments Fraud (PMF)" />
        </Tabs>
      </Paper>

      {subTab === 0 && (
        <EFMTab
          efmData={efmData}
          efmLoading={efmLoading}
          setEfmData={setEfmData}
          setEfmLoading={setEfmLoading}
        />
      )}
      {subTab === 1 && (
        <DBFTab
          dbfData={dbfData}
          dbfLoading={dbfLoading}
          setDbfData={setDbfData}
          setDbfLoading={setDbfLoading}
        />
      )}
      {subTab === 2 && (
        <PMFTab
          pmfData={pmfData}
          pmfLoading={pmfLoading}
          setPmfData={setPmfData}
          setPmfLoading={setPmfLoading}
        />
      )}
    </Box>
  );
}
