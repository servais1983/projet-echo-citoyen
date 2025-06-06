import React, { useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import {
  Grid,
  Paper,
  Typography,
  Box,
  CircularProgress,
} from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from 'chart.js';
import { Line, Pie } from 'react-chartjs-2';
import { fetchDashboardData } from '../store/slices/dashboardSlice';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  ArcElement
);

function Dashboard() {
  const dispatch = useDispatch();
  const { data, loading, error } = useSelector((state) => state.dashboard);

  useEffect(() => {
    dispatch(fetchDashboardData());
  }, [dispatch]);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  const lineChartData = {
    labels: data?.activityData?.labels || [],
    datasets: [
      {
        label: 'Activité',
        data: data?.activityData?.values || [],
        borderColor: 'rgb(75, 192, 192)',
        tension: 0.1,
      },
    ],
  };

  const pieChartData = {
    labels: data?.categoryData?.labels || [],
    datasets: [
      {
        data: data?.categoryData?.values || [],
        backgroundColor: [
          'rgb(255, 99, 132)',
          'rgb(54, 162, 235)',
          'rgb(255, 206, 86)',
          'rgb(75, 192, 192)',
        ],
      },
    ],
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Tableau de bord
      </Typography>

      <Grid container spacing={3}>
        {/* Statistiques rapides */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Requêtes totales
            </Typography>
            <Typography variant="h4">
              {data?.stats?.totalRequests || 0}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Alertes actives
            </Typography>
            <Typography variant="h4">
              {data?.stats?.activeAlerts || 0}
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Taux de satisfaction
            </Typography>
            <Typography variant="h4">
              {data?.stats?.satisfactionRate || 0}%
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Temps de réponse moyen
            </Typography>
            <Typography variant="h4">
              {data?.stats?.avgResponseTime || 0}s
            </Typography>
          </Paper>
        </Grid>

        {/* Graphiques */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Activité récente
            </Typography>
            <Line data={lineChartData} />
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Répartition par catégorie
            </Typography>
            <Pie data={pieChartData} />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}

export default Dashboard; 