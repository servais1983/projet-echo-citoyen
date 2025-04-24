/**
 * Composant principal du tableau de bord ECHO pour les autorités.
 * Affiche une vue consolidée des alertes, incidents et statistiques.
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Container, Row, Col, Card, Button, Badge, Alert, Tabs, Tab, Spinner } from 'react-bootstrap';
import { LineChart, Line, BarChart, Bar, PieChart, Pie, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import AlertMap from './AlertMap';
import AlertList from './AlertList';
import IncidentDetails from './IncidentDetails';
import StatisticsSummary from './StatisticsSummary';
import CitizenFeedback from './CitizenFeedback';
import LiveFeed from './LiveFeed';

// Couleurs pour les graphiques
const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

// Couleurs pour les niveaux de sévérité
const SEVERITY_COLORS = {
  1: '#41AB5D', // Vert
  2: '#A6D96A', // Vert clair
  3: '#FED976', // Jaune
  4: '#FD8D3C', // Orange
  5: '#F03B20'  // Rouge
};

const Dashboard = () => {
  // États pour stocker les données
  const [alerts, setAlerts] = useState([]);
  const [incidents, setIncidents] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [categories, setCategories] = useState([]);
  const [timeSeriesData, setTimeSeriesData] = useState([]);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Onglet actif
  const [activeTab, setActiveTab] = useState('overview');
  
  // Filtres
  const [severityFilter, setSeverityFilter] = useState(null);
  const [categoryFilter, setCategoryFilter] = useState(null);
  const [dateRangeFilter, setDateRangeFilter] = useState('today'); // 'today', 'week', 'month'
  
  // Chargement des données
  useEffect(() => {
    const fetchDashboardData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        // Chargement parallèle des différentes données
        const [alertsResponse, incidentsResponse, statsResponse, categoriesResponse, timeSeriesResponse] = await Promise.all([
          axios.get('/api/alerts/active'),
          axios.get('/api/incidents'),
          axios.get('/api/statistics/summary'),
          axios.get('/api/categories/counts'),
          axios.get(`/api/statistics/time-series?period=${dateRangeFilter}`)
        ]);
        
        setAlerts(alertsResponse.data);
        setIncidents(incidentsResponse.data);
        setStatistics(statsResponse.data);
        setCategories(categoriesResponse.data);
        setTimeSeriesData(timeSeriesResponse.data);
        
      } catch (error) {
        console.error("Erreur lors du chargement des données du tableau de bord", error);
        setError("Erreur lors du chargement des données. Veuillez réessayer plus tard.");
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboardData();
    
    // Mise à jour périodique toutes les minutes
    const intervalId = setInterval(fetchDashboardData, 60000);
    
    // Nettoyage à la destruction du composant
    return () => clearInterval(intervalId);
  }, [dateRangeFilter]);
  
  // Filtrage des alertes selon les critères
  const filteredAlerts = alerts.filter(alert => {
    if (severityFilter && alert.severity !== severityFilter) return false;
    if (categoryFilter && !alert.categories.includes(categoryFilter)) return false;
    return true;
  });
  
  // Gestion de la sélection d'une alerte
  const handleAlertSelect = (alert) => {
    setSelectedAlert(alert);
    
    // Charger automatiquement l'incident lié
    if (alert && alert.incident_id) {
      const incident = incidents.find(inc => inc.incident_id === alert.incident_id);
      if (incident) {
        setSelectedIncident(incident);
      } else {
        // Si l'incident n'est pas déjà chargé, le récupérer via API
        axios.get(`/api/incidents/${alert.incident_id}`)
          .then(response => setSelectedIncident(response.data))
          .catch(err => console.error("Erreur lors du chargement de l'incident", err));
      }
    }
  };
  
  // Gestion de la prise en charge d'une alerte
  const handleAcknowledgeAlert = (alertId) => {
    if (!alertId) return;
    
    axios.post(`/api/alerts/${alertId}/acknowledge`)
      .then(response => {
        // Mettre à jour localement l'état de l'alerte
        const updatedAlerts = alerts.map(alert => 
          alert.alert_id === alertId 
            ? { ...alert, status: 'acknowledged', acknowledged_at: new Date().toISOString() }
            : alert
        );
        setAlerts(updatedAlerts);
        
        // Mettre à jour l'alerte sélectionnée si nécessaire
        if (selectedAlert && selectedAlert.alert_id === alertId) {
          setSelectedAlert({ ...selectedAlert, status: 'acknowledged', acknowledged_at: new Date().toISOString() });
        }
      })
      .catch(error => {
        console.error("Erreur lors de la prise en charge de l'alerte", error);
      });
  };
  
  // Gestion de la résolution d'une alerte
  const handleResolveAlert = (alertId, notes) => {
    if (!alertId) return;
    
    axios.post(`/api/alerts/${alertId}/resolve`, { resolution_notes: notes })
      .then(response => {
        // Mettre à jour localement l'état de l'alerte
        const updatedAlerts = alerts.map(alert => 
          alert.alert_id === alertId 
            ? { ...alert, status: 'resolved', resolved_at: new Date().toISOString(), resolution_notes: notes }
            : alert
        );
        setAlerts(updatedAlerts);
        
        // Mettre à jour l'alerte sélectionnée si nécessaire
        if (selectedAlert && selectedAlert.alert_id === alertId) {
          setSelectedAlert({ 
            ...selectedAlert, 
            status: 'resolved', 
            resolved_at: new Date().toISOString(),
            resolution_notes: notes
          });
        }
      })
      .catch(error => {
        console.error("Erreur lors de la résolution de l'alerte", error);
      });
  };
  
  // Si chargement en cours
  if (loading && !alerts.length) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ height: '80vh' }}>
        <Spinner animation="border" role="status" variant="primary">
          <span className="visually-hidden">Chargement...</span>
        </Spinner>
      </Container>
    );
  }
  
  // Si erreur
  if (error) {
    return (
      <Container className="mt-4">
        <Alert variant="danger">
          {error}
          <Button variant="outline-danger" className="ms-3" onClick={() => window.location.reload()}>
            Réessayer
          </Button>
        </Alert>
      </Container>
    );
  }
  
  return (
    <Container fluid className="dashboard-container py-4">
      {/* En-tête du tableau de bord */}
      <Row className="mb-4">
        <Col>
          <h1 className="dashboard-title">
            Tableau de Bord ECHO
            <Badge bg="primary" className="ms-2">
              {filteredAlerts.filter(a => a.status === 'created').length} alertes actives
            </Badge>
          </h1>
        </Col>
        <Col xs="auto">
          <div className="d-flex">
            <Button 
              variant="outline-secondary" 
              className="me-2"
              onClick={() => setDateRangeFilter('today')}
              active={dateRangeFilter === 'today'}
            >
              Aujourd'hui
            </Button>
            <Button 
              variant="outline-secondary" 
              className="me-2"
              onClick={() => setDateRangeFilter('week')}
              active={dateRangeFilter === 'week'}
            >
              Cette semaine
            </Button>
            <Button 
              variant="outline-secondary"
              onClick={() => setDateRangeFilter('month')}
              active={dateRangeFilter === 'month'}
            >
              Ce mois
            </Button>
          </div>
        </Col>
      </Row>
      
      {/* Onglets principaux */}
      <Tabs
        activeKey={activeTab}
        onSelect={setActiveTab}
        className="mb-4 dashboard-tabs"
      >
        <Tab eventKey="overview" title="Vue d'ensemble">
          <Row>
            {/* Cartes de statistiques */}
            <Col md={8}>
              <Row className="mb-4">
                <Col md={3}>
                  <Card className="dashboard-stat-card">
                    <Card.Body>
                      <Card.Title>Alertes actives</Card.Title>
                      <h2 className="stat-number">{statistics.activeAlerts || 0}</h2>
                      <p className={`trend ${statistics.alertsTrend > 0 ? 'up' : 'down'}`}>
                        {statistics.alertsTrend > 0 ? '+' : ''}{statistics.alertsTrend || 0}% depuis hier
                      </p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="dashboard-stat-card">
                    <Card.Body>
                      <Card.Title>Incidents ouverts</Card.Title>
                      <h2 className="stat-number">{statistics.openIncidents || 0}</h2>
                      <p className={`trend ${statistics.incidentsTrend > 0 ? 'up' : 'down'}`}>
                        {statistics.incidentsTrend > 0 ? '+' : ''}{statistics.incidentsTrend || 0}% depuis hier
                      </p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="dashboard-stat-card">
                    <Card.Body>
                      <Card.Title>Résolutions</Card.Title>
                      <h2 className="stat-number">{statistics.resolutionsToday || 0}</h2>
                      <p>Aujourd'hui</p>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={3}>
                  <Card className="dashboard-stat-card">
                    <Card.Body>
                      <Card.Title>Temps moyen</Card.Title>
                      <h2 className="stat-number">{statistics.avgResolutionTime || '0h'}</h2>
                      <p>de résolution</p>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
              
              {/* Graphique d'évolution */}
              <Card className="mb-4">
                <Card.Header>Évolution des alertes</Card.Header>
                <Card.Body>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={timeSeriesData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="alerts" stroke="#8884d8" name="Alertes" />
                      <Line type="monotone" dataKey="incidents" stroke="#82ca9d" name="Incidents" />
                      <Line type="monotone" dataKey="resolutions" stroke="#ffc658" name="Résolutions" />
                    </LineChart>
                  </ResponsiveContainer>
                </Card.Body>
              </Card>
              
              {/* Distribution par catégorie */}
              <Row>
                <Col md={6}>
                  <Card className="mb-4">
                    <Card.Header>Distribution par catégorie</Card.Header>
                    <Card.Body>
                      <ResponsiveContainer width="100%" height={300}>
                        <PieChart>
                          <Pie
                            data={categories}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            outerRadius={80}
                            fill="#8884d8"
                            dataKey="count"
                            nameKey="name"
                            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                          >
                            {categories.map((entry, index) => (
                              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                            ))}
                          </Pie>
                          <Tooltip formatter={(value, name) => [value, name]} />
                        </PieChart>
                      </ResponsiveContainer>
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={6}>
                  <Card className="mb-4">
                    <Card.Header>Distribution par sévérité</Card.Header>
                    <Card.Body>
                      <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={[
                          { name: 'Niveau 1', count: statistics.severityDistribution?.[1] || 0 },
                          { name: 'Niveau 2', count: statistics.severityDistribution?.[2] || 0 },
                          { name: 'Niveau 3', count: statistics.severityDistribution?.[3] || 0 },
                          { name: 'Niveau 4', count: statistics.severityDistribution?.[4] || 0 },
                          { name: 'Niveau 5', count: statistics.severityDistribution?.[5] || 0 }
                        ]}>
                          <CartesianGrid strokeDasharray="3 3" />
                          <XAxis dataKey="name" />
                          <YAxis />
                          <Tooltip />
                          <Bar dataKey="count" name="Nombre d'alertes">
                            {[1, 2, 3, 4, 5].map((severity, index) => (
                              <Cell key={`cell-${index}`} fill={SEVERITY_COLORS[severity+1] || COLORS[index]} />
                            ))}
                          </Bar>
                        </BarChart>
                      </ResponsiveContainer>
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </Col>
            
            {/* Liste d'alertes */}
            <Col md={4}>
              <Card className="dashboard-alerts-card">
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <span>Alertes récentes</span>
                  <div>
                    <Button 
                      variant="outline-secondary" 
                      size="sm"
                      onClick={() => setSeverityFilter(null)}
                      active={severityFilter === null}
                      className="me-1"
                    >
                      Tous
                    </Button>
                    {[5, 4, 3].map(level => (
                      <Button
                        key={level}
                        variant="outline-secondary"
                        size="sm"
                        style={{ 
                          borderColor: SEVERITY_COLORS[level],
                          color: severityFilter === level ? 'white' : SEVERITY_COLORS[level],
                          backgroundColor: severityFilter === level ? SEVERITY_COLORS[level] : 'transparent'
                        }}
                        onClick={() => setSeverityFilter(severityFilter === level ? null : level)}
                        className="me-1"
                      >
                        Niveau {level}
                      </Button>
                    ))}
                  </div>
                </Card.Header>
                <Card.Body style={{ maxHeight: '800px', overflowY: 'auto' }}>
                  <AlertList 
                    alerts={filteredAlerts} 
                    onSelect={handleAlertSelect}
                    onAcknowledge={handleAcknowledgeAlert}
                    onResolve={handleResolveAlert}
                    selectedAlertId={selectedAlert?.alert_id}
                  />
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
        
        <Tab eventKey="map" title="Carte des alertes">
          <Card className="mb-4">
            <Card.Body>
              <AlertMap 
                width="100%" 
                height={600}
                onAlertSelect={handleAlertSelect}
              />
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="incidents" title="Gestion des incidents">
          <Row>
            <Col md={6}>
              <Card className="mb-4">
                <Card.Header>Liste des incidents</Card.Header>
                <Card.Body style={{ maxHeight: '600px', overflowY: 'auto' }}>
                  {/* Liste des incidents ici */}
                </Card.Body>
              </Card>
            </Col>
            <Col md={6}>
              <Card className="mb-4">
                <Card.Header>Détails de l'incident</Card.Header>
                <Card.Body>
                  {selectedIncident ? (
                    <IncidentDetails incident={selectedIncident} />
                  ) : (
                    <div className="text-center p-5 text-muted">
                      Sélectionnez un incident pour voir les détails
                    </div>
                  )}
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Tab>
        
        <Tab eventKey="feedback" title="Retour citoyens">
          <Card className="mb-4">
            <Card.Header>Retours des citoyens</Card.Header>
            <Card.Body>
              <CitizenFeedback />
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="live" title="Flux en direct">
          <Card className="mb-4">
            <Card.Header>Flux de données en temps réel</Card.Header>
            <Card.Body>
              <LiveFeed />
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
      
      {/* Pied de page */}
      <footer className="text-center text-muted mt-5">
        <p>Projet ECHO - Tableau de bord d'administration pour les autorités</p>
        <p>Version 1.0 - {new Date().getFullYear()}</p>
      </footer>
    </Container>
  );
};

export default Dashboard;