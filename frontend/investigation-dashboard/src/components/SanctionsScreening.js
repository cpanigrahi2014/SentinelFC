import React, { useState } from 'react';
import {
  Box, Card, CardContent, Typography, TextField, Button, Grid,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Chip, CircularProgress, Paper, Alert,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import { screenEntity } from '../services/api';
import { useSnackbar } from 'notistack';

export default function SanctionsScreening() {
  const [query, setQuery] = useState({ name: '', entity_type: 'individual', country: '' });
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const { enqueueSnackbar } = useSnackbar();

  const handleScreen = async () => {
    if (!query.name.trim()) return;
    setLoading(true);
    try {
      const res = await screenEntity({
        name: query.name,
        entity_type: query.entity_type,
        country: query.country || undefined,
      });
      setResults(res.data);
    } catch (err) {
      enqueueSnackbar('Screening failed', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const matches = results?.matches || results?.results || [];
  const isMatch = results?.is_match || matches.length > 0;

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>Sanctions Screening</Typography>

      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>Screen Entity</Typography>
          <Grid container spacing={2} alignItems="flex-end">
            <Grid item xs={12} sm={4}>
              <TextField fullWidth label="Name" value={query.name} required
                onChange={(e) => setQuery({ ...query, name: e.target.value })}
                onKeyDown={(e) => e.key === 'Enter' && handleScreen()}
              />
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField select fullWidth label="Entity Type" value={query.entity_type}
                onChange={(e) => setQuery({ ...query, entity_type: e.target.value })}
                SelectProps={{ native: true }}>
                <option value="individual">Individual</option>
                <option value="organization">Organization</option>
                <option value="vessel">Vessel</option>
              </TextField>
            </Grid>
            <Grid item xs={12} sm={3}>
              <TextField fullWidth label="Country (optional)" value={query.country}
                onChange={(e) => setQuery({ ...query, country: e.target.value })} />
            </Grid>
            <Grid item xs={12} sm={2}>
              <Button fullWidth variant="contained" startIcon={<SearchIcon />}
                onClick={handleScreen} disabled={loading || !query.name.trim()}
                sx={{ height: 56 }}>
                {loading ? <CircularProgress size={24} /> : 'Screen'}
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {results && (
        <Card>
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Screening Results</Typography>
              <Chip
                label={isMatch ? `${matches.length} Match(es) Found` : 'No Matches'}
                color={isMatch ? 'error' : 'success'}
              />
            </Box>

            {isMatch ? (
              <TableContainer component={Paper} variant="outlined">
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Source</TableCell>
                      <TableCell>Score</TableCell>
                      <TableCell>Country</TableCell>
                      <TableCell>Programs</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {matches.map((match, i) => (
                      <TableRow key={i}>
                        <TableCell>{match.matched_name || match.name}</TableCell>
                        <TableCell>
                          <Chip label={match.source || match.list_type || 'Unknown'} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={`${((match.score || match.match_score || 0) * 100).toFixed(0)}%`}
                            size="small"
                            color={match.score >= 0.95 ? 'error' : match.score >= 0.85 ? 'warning' : 'info'}
                          />
                        </TableCell>
                        <TableCell>{match.country || 'N/A'}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {(match.programs || match.sanctions_programs || []).map((p, j) => (
                              <Chip key={j} label={p} size="small" variant="outlined" />
                            ))}
                          </Box>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            ) : (
              <Alert severity="success">
                No sanctions matches found for "{query.name}". Entity cleared.
              </Alert>
            )}
          </CardContent>
        </Card>
      )}
    </Box>
  );
}
