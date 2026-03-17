import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar, Box, CssBaseline, Drawer, IconButton, List, ListItem,
  ListItemButton, ListItemIcon, ListItemText, Toolbar, Typography,
  Avatar, Menu, MenuItem, Divider, Chip,
} from '@mui/material';
import MenuIcon from '@mui/icons-material/Menu';
import DashboardIcon from '@mui/icons-material/Dashboard';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import FolderIcon from '@mui/icons-material/Folder';
import HubIcon from '@mui/icons-material/Hub';
import GppBadIcon from '@mui/icons-material/GppBad';
import AssessmentIcon from '@mui/icons-material/Assessment';
import HistoryIcon from '@mui/icons-material/History';
import LogoutIcon from '@mui/icons-material/Logout';
import StorageIcon from '@mui/icons-material/Storage';
import AdminPanelSettingsIcon from '@mui/icons-material/AdminPanelSettings';
import GavelIcon from '@mui/icons-material/Gavel';
import ShieldIcon from '@mui/icons-material/Shield';
import VerifiedUserIcon from '@mui/icons-material/VerifiedUser';
import WorkIcon from '@mui/icons-material/Work';
import PsychologyIcon from '@mui/icons-material/Psychology';
import { useAuth } from '../contexts/AuthContext';

const DRAWER_WIDTH = 260;

const navItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Alerts', icon: <NotificationsActiveIcon />, path: '/alerts' },
  { text: 'Cases', icon: <FolderIcon />, path: '/cases' },
  { text: 'Network Analytics', icon: <HubIcon />, path: '/network' },
  { text: 'Sanctions Screening', icon: <GppBadIcon />, path: '/sanctions' },
  { text: 'Regulatory Reports', icon: <AssessmentIcon />, path: '/reports' },
  { text: 'Audit Logs', icon: <HistoryIcon />, path: '/audit' },
  { divider: true, label: 'Financial Crime' },
  { text: 'AML', icon: <GavelIcon />, path: '/aml' },
  { text: 'Fraud Management', icon: <ShieldIcon />, path: '/fraud' },
  { text: 'KYC / CDD', icon: <VerifiedUserIcon />, path: '/kyc' },
  { text: 'ActOne', icon: <WorkIcon />, path: '/actone' },
  { text: 'AI/ML Analytics', icon: <PsychologyIcon />, path: '/aiml' },
  { divider: true, label: 'Administration' },
  { text: 'Data Sources', icon: <StorageIcon />, path: '/admin/data-sources' },
];

export default function Layout({ children }) {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState(null);
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const drawer = (
    <Box>
      <Toolbar sx={{ justifyContent: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 700, color: 'primary.main' }}>
          SENTINELFC
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        {navItems.map((item, idx) => {
          if (item.divider) {
            return (
              <React.Fragment key={item.label}>
                <Divider sx={{ my: 1 }} />
                <ListItem disablePadding sx={{ px: 2, pt: 1 }}>
                  <Typography variant="caption" color="text.secondary" fontWeight={600}>
                    {item.label}
                  </Typography>
                </ListItem>
              </React.Fragment>
            );
          }
          return (
            <ListItem key={item.text} disablePadding>
              <ListItemButton
                selected={location.pathname === item.path}
                onClick={() => { navigate(item.path); setMobileOpen(false); }}
                sx={{
                  mx: 1, borderRadius: 2, mb: 0.5,
                  '&.Mui-selected': { bgcolor: 'primary.main', color: 'white',
                    '& .MuiListItemIcon-root': { color: 'white' } },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>{item.icon}</ListItemIcon>
                <ListItemText primary={item.text} />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1, bgcolor: 'white', color: 'text.primary' }} elevation={1}>
        <Toolbar>
          <IconButton edge="start" onClick={() => setMobileOpen(!mobileOpen)} sx={{ mr: 2, display: { md: 'none' } }}>
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap sx={{ flexGrow: 1 }}>
            Investigation Dashboard
          </Typography>
          <Chip label={user?.role?.replace('_', ' ')} size="small" color="primary" variant="outlined" sx={{ mr: 2, textTransform: 'capitalize' }} />
          <IconButton onClick={(e) => setAnchorEl(e.currentTarget)}>
            <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main', fontSize: 14 }}>
              {user?.username?.charAt(0).toUpperCase()}
            </Avatar>
          </IconButton>
          <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
            <MenuItem disabled>
              <Typography variant="body2">{user?.username}</Typography>
            </MenuItem>
            <Divider />
            <MenuItem onClick={() => { setAnchorEl(null); logout(); navigate('/login'); }}>
              <ListItemIcon><LogoutIcon fontSize="small" /></ListItemIcon>
              Logout
            </MenuItem>
          </Menu>
        </Toolbar>
      </AppBar>

      <Drawer variant="temporary" open={mobileOpen} onClose={() => setMobileOpen(false)}
        sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH } }}>
        {drawer}
      </Drawer>
      <Drawer variant="permanent"
        sx={{ display: { xs: 'none', md: 'block' }, '& .MuiDrawer-paper': { width: DRAWER_WIDTH, boxSizing: 'border-box' } }}>
        {drawer}
      </Drawer>

      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8, ml: { md: `${DRAWER_WIDTH}px` }, minHeight: '100vh' }}>
        {children}
      </Box>
    </Box>
  );
}
