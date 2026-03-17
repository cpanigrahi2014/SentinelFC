import React, { useState } from 'react';
import { Box, Typography, Paper, Tabs, Tab } from '@mui/material';
import GavelIcon from '@mui/icons-material/Gavel';
import SecurityIcon from '@mui/icons-material/Security';
import PersonSearchIcon from '@mui/icons-material/PersonSearch';
import FilterListIcon from '@mui/icons-material/FilterList';
import { CapabilitiesTab, CDDTab, WLFTab } from './DataSources';

export default function AMLPage() {
  const [subTab, setSubTab] = useState(0);
  const [capabilitiesData, setCapabilitiesData] = useState(null);
  const [capabilitiesLoading, setCapabilitiesLoading] = useState(false);
  const [cddData, setCddData] = useState(null);
  const [cddLoading, setCddLoading] = useState(false);
  const [wlfData, setWlfData] = useState(null);
  const [wlfLoading, setWlfLoading] = useState(false);

  return (
    <Box>
      <Box display="flex" alignItems="center" gap={1.5} mb={2}>
        <GavelIcon sx={{ fontSize: 32, color: 'primary.main' }} />
        <Box>
          <Typography variant="h5" fontWeight={700}>Anti-Money Laundering (AML)</Typography>
          <Typography variant="body2" color="text.secondary">
            Comprehensive AML compliance &mdash; Key Capabilities, Customer Due Diligence &amp; Watchlist Filtering
          </Typography>
        </Box>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Tabs value={subTab} onChange={(_, v) => setSubTab(v)} variant="scrollable" scrollButtons="auto"
          sx={{ '& .MuiTab-root': { fontWeight: 600 } }}>
          <Tab icon={<SecurityIcon />} iconPosition="start" label="Key Capabilities" />
          <Tab icon={<PersonSearchIcon />} iconPosition="start" label="CDD / EDD" />
          <Tab icon={<FilterListIcon />} iconPosition="start" label="Watchlist Filtering" />
        </Tabs>
      </Paper>

      {subTab === 0 && (
        <CapabilitiesTab
          capabilitiesData={capabilitiesData}
          capabilitiesLoading={capabilitiesLoading}
          setCapabilitiesData={setCapabilitiesData}
          setCapabilitiesLoading={setCapabilitiesLoading}
        />
      )}
      {subTab === 1 && (
        <CDDTab
          cddData={cddData}
          cddLoading={cddLoading}
          setCddData={setCddData}
          setCddLoading={setCddLoading}
        />
      )}
      {subTab === 2 && (
        <WLFTab
          wlfData={wlfData}
          wlfLoading={wlfLoading}
          setWlfData={setWlfData}
          setWlfLoading={setWlfLoading}
        />
      )}
    </Box>
  );
}
