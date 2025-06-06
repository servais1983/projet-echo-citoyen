import logging
import sys
from logging.handlers import RotatingFileHandler
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Formateur de logs au format JSON"""
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Ajouter les données supplémentaires si présentes
        if hasattr(record, "extra"):
            log_record.update(record.extra)
        
        # Ajouter l'exception si présente
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_record)

def setup_logging():
    """Configuration du système de logging"""
    # Configuration du logger principal
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Handler pour la console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    
    # Handler pour le fichier
    file_handler = RotatingFileHandler(
        'logs/notifications.log',
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(JSONFormatter())
    
    # Ajout des handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Configuration des loggers spécifiques
    loggers = {
        'uvicorn': logging.INFO,
        'uvicorn.access': logging.INFO,
        'uvicorn.error': logging.ERROR,
        'sqlalchemy.engine': logging.WARNING,
        'fastapi': logging.INFO
    }
    
    for logger_name, level in loggers.items():
        logging.getLogger(logger_name).setLevel(level)
    
    return logger

# Middleware pour le logging des requêtes
class RequestLoggingMiddleware:
    def __init__(self, app):
        self.app = app
        self.logger = logging.getLogger("request_logger")
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        
        start_time = datetime.utcnow()
        
        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                process_time = (datetime.utcnow() - start_time).total_seconds()
                self.logger.info(
                    "Request processed",
                    extra={
                        "method": scope["method"],
                        "path": scope["path"],
                        "status_code": message["status"],
                        "process_time": process_time,
                        "client_ip": scope.get("client", ("", 0))[0]
                    }
                )
            await send(message)
        
        return await self.app(scope, receive, send_wrapper)

# Fonction pour logger les erreurs
def log_error(error, context=None):
    """Log une erreur avec son contexte"""
    logger = logging.getLogger("error_logger")
    extra = {"error_type": type(error).__name__}
    if context:
        extra.update(context)
    
    logger.error(
        str(error),
        exc_info=True,
        extra=extra
    )

# Fonction pour logger les métriques
def log_metric(name, value, tags=None):
    """Log une métrique avec ses tags"""
    logger = logging.getLogger("metric_logger")
    extra = {"metric_name": name, "metric_value": value}
    if tags:
        extra.update(tags)
    
    logger.info(
        f"Metric: {name} = {value}",
        extra=extra
    ) 