/**
 * Composant de liste d'alertes pour le tableau de bord ECHO.
 * Affiche les alertes sous forme de liste et permet d'interagir avec elles.
 */

import React from 'react';
import { Card, Badge, Button, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { Check, Alert, Bookmark, CheckSquare, Eye, XSquare } from 'react-bootstrap-icons';

// Couleurs pour les niveaux de sévérité
const SEVERITY_COLORS = {
  1: '#41AB5D', // Vert
  2: '#A6D96A', // Vert clair
  3: '#FED976', // Jaune
  4: '#FD8D3C', // Orange
  5: '#F03B20'  // Rouge
};

// Étiquettes pour les niveaux de sévérité
const SEVERITY_LABELS = {
  1: "Information",
  2: "Attention",
  3: "Intervention",
  4: "Urgence",
  5: "Critique"
};

// Icônes pour les statuts
const STATUS_ICONS = {
  "created": <Alert size={16} className="text-danger" />,
  "notified": <Bookmark size={16} className="text-warning" />,
  "acknowledged": <Eye size={16} className="text-primary" />,
  "resolved": <CheckSquare size={16} className="text-success" />
};

const AlertList = ({ alerts, onSelect, onAcknowledge, onResolve, selectedAlertId }) => {
  // Tri des alertes par sévérité décroissante, puis par date
  const sortedAlerts = [...alerts].sort((a, b) => {
    // D'abord par statut (créé > notifié > pris en charge > résolu)
    const statusOrder = { created: 0, notified: 1, acknowledged: 2, resolved: 3 };
    const statusDiff = statusOrder[a.status] - statusOrder[b.status];
    if (statusDiff !== 0) return statusDiff;
    
    // Ensuite par sévérité (5 > 4 > 3 > 2 > 1)
    const severityDiff = b.severity - a.severity;
    if (severityDiff !== 0) return severityDiff;
    
    // Enfin par date (plus récent d'abord)
    return new Date(b.created_at) - new Date(a.created_at);
  });
  
  // Formatage de la date pour affichage
  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    
    // Si c'est aujourd'hui, afficher l'heure
    if (date.toDateString() === now.toDateString()) {
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    // Sinon, afficher la date au format court
    return date.toLocaleDateString();
  };
  
  // Fonction pour tronquer le texte long
  const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
  };
  
  // Rendu d'une alerte individuelle
  const renderAlert = (alert) => {
    const isSelected = selectedAlertId === alert.alert_id;
    const isResolved = alert.status === 'resolved';
    
    return (
      <Card 
        key={alert.alert_id} 
        className={`mb-3 alert-card ${isSelected ? 'border-primary' : ''}`}
        style={{ 
          borderLeft: `5px solid ${SEVERITY_COLORS[alert.severity] || '#ccc'}`,
          opacity: isResolved ? 0.7 : 1,
          backgroundColor: isSelected ? '#f0f8ff' : 'white'
        }}
        onClick={() => onSelect(alert)}
      >
        <Card.Body className="p-3">
          <div className="d-flex justify-content-between align-items-start">
            <div>
              <div className="d-flex align-items-center mb-2">
                {STATUS_ICONS[alert.status]}
                <span className="ms-2 text-muted small">
                  {formatDate(alert.created_at)}
                </span>
                <Badge 
                  bg="light" 
                  text="dark" 
                  className="ms-2"
                  style={{ 
                    backgroundColor: SEVERITY_COLORS[alert.severity], 
                    opacity: 0.2,
                    color: SEVERITY_COLORS[alert.severity]
                  }}
                >
                  {SEVERITY_LABELS[alert.severity]}
                </Badge>
              </div>
              <Card.Title as="h6" className="mb-2">{truncateText(alert.summary, 60)}</Card.Title>
              
              {/* Catégories */}
              <div className="mb-2">
                {alert.categories && alert.categories.map((category, idx) => (
                  <Badge 
                    key={idx} 
                    bg="light" 
                    text="dark" 
                    pill
                    className="me-1"
                  >
                    {category}
                  </Badge>
                ))}
              </div>
              
              {/* Localisation */}
              {alert.location && (
                <div className="small text-muted">
                  <i className="bi bi-geo-alt"></i> {alert.location_text || "Localisation disponible"}
                </div>
              )}
            </div>
            
            {/* Actions */}
            <div className="d-flex">
              {alert.status === 'created' || alert.status === 'notified' ? (
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip>Prendre en charge</Tooltip>}
                >
                  <Button 
                    variant="outline-primary" 
                    size="sm" 
                    className="me-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      onAcknowledge(alert.alert_id);
                    }}
                  >
                    <Check size={16} />
                  </Button>
                </OverlayTrigger>
              ) : null}
              
              {alert.status !== 'resolved' ? (
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip>Marquer comme résolu</Tooltip>}
                >
                  <Button 
                    variant="outline-success" 
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation();
                      // Simuler une note de résolution pour l'exemple
                      // Dans un cas réel, ouvrir une modal pour demander une note
                      onResolve(alert.alert_id, "Problème résolu par les services techniques.");
                    }}
                  >
                    <CheckSquare size={16} />
                  </Button>
                </OverlayTrigger>
              ) : (
                <OverlayTrigger
                  placement="top"
                  overlay={<Tooltip>Résolu le {formatDate(alert.resolved_at)}</Tooltip>}
                >
                  <span className="text-success">
                    <CheckSquare size={16} />
                  </span>
                </OverlayTrigger>
              )}
            </div>
          </div>
          
          {/* Affichage conditionnel de plus d'informations si sélectionné */}
          {isSelected && (
            <div className="mt-3 pt-3 border-top">
              <p className="small text-muted mb-2">
                {alert.description || "Pas de description détaillée disponible."}
              </p>
              
              {alert.status === 'acknowledged' && (
                <div className="small text-primary">
                  <i className="bi bi-person-check"></i> Pris en charge le {formatDate(alert.acknowledged_at)}
                </div>
              )}
              
              {alert.status === 'resolved' && alert.resolution_notes && (
                <div className="small mt-2">
                  <strong>Note de résolution:</strong> {alert.resolution_notes}
                </div>
              )}
            </div>
          )}
        </Card.Body>
      </Card>
    );
  };
  
  return (
    <div className="alert-list">
      {sortedAlerts.length === 0 ? (
        <div className="text-center p-4 text-muted">
          <XSquare size={32} className="mb-2" />
          <p>Aucune alerte à afficher</p>
        </div>
      ) : (
        sortedAlerts.map(renderAlert)
      )}
    </div>
  );
};

export default AlertList;