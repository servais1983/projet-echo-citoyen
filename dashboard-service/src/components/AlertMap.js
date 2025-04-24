/**
 * Composant de carte interactive des alertes pour le tableau de bord ECHO.
 * Affiche les alertes et incidents géolocalisés sur une carte avec code couleur
 * selon la sévérité et permet d'interagir avec eux.
 */

import React, { useState, useEffect } from 'react';
import { DeckGL, ScatterplotLayer, GeoJsonLayer } from 'deck.gl';
import { StaticMap } from 'react-map-gl';
import { IconLayer } from '@deck.gl/layers';
import { WebMercatorViewport } from '@deck.gl/core';
import axios from 'axios';

// Remplacer par une vraie clé d'API en production
const MAPBOX_ACCESS_TOKEN = 'XXXXX';

// Couleurs pour les différents niveaux d'alerte
const SEVERITY_COLORS = {
  1: [65, 171, 93],    // Vert - Information
  2: [166, 217, 106],  // Vert clair - Attention
  3: [254, 217, 118],  // Jaune - Intervention
  4: [253, 141, 60],   // Orange - Urgence
  5: [240, 59, 32]     // Rouge - Critique
};

const AlertMap = ({ width, height, onAlertSelect }) => {
  // État pour stocker les données des alertes
  const [alerts, setAlerts] = useState([]);
  
  // État pour stocker les données des services d'urgence
  const [emergencyServices, setEmergencyServices] = useState([]);
  
  // Vue initiale de la carte
  const [viewport, setViewport] = useState({
    longitude: 2.333333,  // Coordonnées centrées sur la France
    latitude: 48.866667,
    zoom: 5,
    pitch: 0,
    bearing: 0
  });
  
  // Alerte sélectionnée
  const [selectedAlert, setSelectedAlert] = useState(null);
  
  // Chargement des alertes depuis l'API
  useEffect(() => {
    const fetchAlerts = async () => {
      try {
        const response = await axios.get('/api/alerts/active');
        setAlerts(response.data);
        
        // Ajuster la vue de la carte si des alertes sont présentes
        if (response.data.length > 0) {
          fitBoundsToAlerts(response.data);
        }
      } catch (error) {
        console.error("Erreur lors du chargement des alertes", error);
      }
    };
    
    const fetchEmergencyServices = async () => {
      try {
        const response = await axios.get('/api/emergency-services');
        setEmergencyServices(response.data);
      } catch (error) {
        console.error("Erreur lors du chargement des services d'urgence", error);
      }
    };
    
    // Chargement initial
    fetchAlerts();
    fetchEmergencyServices();
    
    // Mise à jour périodique toutes les 30 secondes
    const intervalId = setInterval(fetchAlerts, 30000);
    
    // Nettoyage à la destruction du composant
    return () => clearInterval(intervalId);
  }, []);
  
  // Ajuste la vue de la carte pour afficher toutes les alertes
  const fitBoundsToAlerts = (alertsData) => {
    // Filtrer les alertes qui ont des coordonnées
    const geoAlerts = alertsData.filter(alert => 
      alert.location && alert.location.lat && alert.location.lng
    );
    
    if (geoAlerts.length === 0) return;
    
    // Déterminer les limites (bounds) des alertes
    let minLat = Infinity;
    let maxLat = -Infinity;
    let minLng = Infinity;
    let maxLng = -Infinity;
    
    geoAlerts.forEach(alert => {
      minLat = Math.min(minLat, alert.location.lat);
      maxLat = Math.max(maxLat, alert.location.lat);
      minLng = Math.min(minLng, alert.location.lng);
      maxLng = Math.max(maxLng, alert.location.lng);
    });
    
    // Ajouter une marge
    const PADDING = 0.1;
    minLat -= PADDING;
    maxLat += PADDING;
    minLng -= PADDING;
    maxLng += PADDING;
    
    // Calculer la nouvelle vue
    const newViewport = new WebMercatorViewport({ width, height })
      .fitBounds(
        [[minLng, minLat], [maxLng, maxLat]],
        { padding: 40 }
      );
    
    setViewport({
      longitude: newViewport.longitude,
      latitude: newViewport.latitude,
      zoom: newViewport.zoom,
      pitch: 0,
      bearing: 0
    });
  };
  
  // Gestionnaire de clic sur une alerte
  const handleAlertClick = (info) => {
    const alert = info.object;
    setSelectedAlert(alert);
    if (onAlertSelect) {
      onAlertSelect(alert);
    }
  };
  
  // Couche pour afficher les alertes
  const alertsLayer = new ScatterplotLayer({
    id: 'alerts',
    data: alerts,
    pickable: true,
    opacity: 0.8,
    stroked: true,
    filled: true,
    radiusScale: 6,
    radiusMinPixels: 6,
    radiusMaxPixels: 30,
    lineWidthMinPixels: 1,
    getPosition: d => [d.location.lng, d.location.lat],
    getRadius: d => Math.sqrt(d.severity) * 3000,
    getFillColor: d => SEVERITY_COLORS[d.severity] || SEVERITY_COLORS[1],
    getLineColor: d => selectedAlert && d.alert_id === selectedAlert.alert_id 
      ? [255, 255, 255]  // Blanc pour l'alerte sélectionnée
      : [0, 0, 0, 80],   // Noir transparent pour les autres
    lineWidthScale: 1,
    onHover: (info) => {
      // Changer le curseur au survol
      if (info.object) {
        info.target.getCanvas().style.cursor = 'pointer';
      } else {
        info.target.getCanvas().style.cursor = 'grab';
      }
    },
    onClick: handleAlertClick,
    updateTriggers: {
      getLineColor: [selectedAlert]
    }
  });
  
  // Couche pour afficher les services d'urgence
  const emergencyServicesLayer = new IconLayer({
    id: 'emergency-services',
    data: emergencyServices,
    pickable: true,
    iconAtlas: '/assets/emergency-icons-atlas.png',
    iconMapping: {
      'police': {x: 0, y: 0, width: 64, height: 64},
      'fire': {x: 64, y: 0, width: 64, height: 64},
      'ambulance': {x: 128, y: 0, width: 64, height: 64},
      'hospital': {x: 192, y: 0, width: 64, height: 64},
      'infrastructure': {x: 256, y: 0, width: 64, height: 64}
    },
    sizeScale: 15,
    getPosition: d => [d.location.lng, d.location.lat],
    getIcon: d => d.type || 'infrastructure',
    getSize: d => 3,
    getColor: [255, 255, 255]
  });
  
  // Gestionnaire de changement de vue
  const onViewStateChange = ({ viewState }) => {
    setViewport(viewState);
  };
  
  return (
    <div style={{ position: 'relative', width, height }}>
      <DeckGL
        layers={[alertsLayer, emergencyServicesLayer]}
        initialViewState={viewport}
        onViewStateChange={onViewStateChange}
        controller={true}
        getTooltip={({ object }) => object && `
          ${object.summary || object.name}
          ${object.severity ? `\nNiveau: ${object.severity} (${object.severity_label})` : ''}
          ${object.created_at ? `\nCréé le: ${new Date(object.created_at).toLocaleString()}` : ''}
        `}
      >
        <StaticMap
          mapboxApiAccessToken={MAPBOX_ACCESS_TOKEN}
          mapStyle="mapbox://styles/mapbox/dark-v10"
        />
      </DeckGL>
      
      {/* Légende de la carte */}
      <div className="map-legend" style={{
        position: 'absolute',
        bottom: 20,
        right: 20,
        backgroundColor: 'rgba(255, 255, 255, 0.8)',
        padding: '10px',
        borderRadius: '5px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.3)'
      }}>
        <h4 style={{ margin: '0 0 10px 0' }}>Sévérité des alertes</h4>
        {Object.entries(SEVERITY_COLORS).map(([level, color]) => (
          <div key={level} style={{ display: 'flex', alignItems: 'center', marginBottom: '5px' }}>
            <div style={{
              width: '20px',
              height: '20px',
              backgroundColor: `rgb(${color.join(',')})`,
              borderRadius: '50%',
              marginRight: '10px'
            }} />
            <span>Niveau {level} - {getAlertLevelName(level)}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

// Fonction utilitaire pour obtenir le nom d'un niveau d'alerte
const getAlertLevelName = (level) => {
  const levels = {
    1: "Information",
    2: "Attention",
    3: "Intervention",
    4: "Urgence",
    5: "Critique"
  };
  return levels[level] || "Inconnu";
};

export default AlertMap;
