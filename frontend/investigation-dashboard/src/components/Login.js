import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box, Card, CardContent, TextField, Button, Typography, Alert, Avatar,
  Container, CircularProgress,
} from '@mui/material';
import LockOutlinedIcon from '@mui/icons-material/LockOutlined';
import { useAuth } from '../contexts/AuthContext';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      await login(username, password);
      navigate('/');
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="sm">
      <Box sx={{ mt: { xs: 4, sm: 8, md: 12 }, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Avatar sx={{ m: 1, bgcolor: 'primary.main', width: 56, height: 56 }}>
          <LockOutlinedIcon />
        </Avatar>
        <Typography variant="h4" sx={{ mb: 1, fontWeight: 700 }}>SentinelFC</Typography>
        <Typography variant="subtitle1" color="text.secondary" sx={{ mb: 3 }}>
          Financial Crime Investigation Platform
        </Typography>
        <Card sx={{ width: '100%' }}>
          <CardContent sx={{ p: { xs: 2, sm: 3, md: 4 } }}>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            <form onSubmit={handleSubmit}>
              <TextField
                fullWidth label="Username" margin="normal" required
                value={username} onChange={(e) => setUsername(e.target.value)}
                autoFocus autoComplete="username"
              />
              <TextField
                fullWidth label="Password" type="password" margin="normal" required
                value={password} onChange={(e) => setPassword(e.target.value)}
                autoComplete="current-password"
              />
              <Button
                type="submit" fullWidth variant="contained" size="large"
                sx={{ mt: 3, mb: 2 }} disabled={loading}
              >
                {loading ? <CircularProgress size={24} /> : 'Sign In'}
              </Button>
            </form>
            <Typography variant="body2" color="text.secondary" align="center">
              Demo: admin / admin123 | analyst / analyst123
            </Typography>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
}
