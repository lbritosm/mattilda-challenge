"""
Módulo de cache con Redis para optimizar consultas pesadas.
"""
import json
import logging
from typing import Optional, Any
from functools import wraps
import redis
from app.core.config import settings

logger = logging.getLogger(__name__)

# Cliente Redis (singleton)
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Obtiene el cliente Redis (singleton).
    Retorna None si Redis no está disponible.
    """
    global _redis_client
    
    if _redis_client is not None:
        return _redis_client
    
    try:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            socket_connect_timeout=2,
            socket_timeout=2
        )
        # Test de conexión
        _redis_client.ping()
        logger.info("Redis cache conectado exitosamente")
        return _redis_client
    except Exception as e:
        logger.warning(f"Redis no disponible: {e}. Cache deshabilitado.")
        _redis_client = None
        return None


def cache_statement(key: str, ttl: int = 60):
    """
    Decorador para cachear resultados de statements.
    
    Args:
        key: Patrón de clave (puede incluir {student_id} o {school_id})
        ttl: Tiempo de vida en segundos (default: 60)
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Construir clave de cache
            cache_key = key.format(**kwargs)
            
            # Intentar obtener de cache
            redis_client = get_redis_client()
            if redis_client:
                try:
                    cached = redis_client.get(cache_key)
                    if cached:
                        logger.debug(f"Cache hit: {cache_key}")
                        return json.loads(cached)
                except Exception as e:
                    logger.warning(f"Error leyendo cache: {e}")
            
            # Si no está en cache, ejecutar función
            logger.debug(f"Cache miss: {cache_key}")
            result = await func(*args, **kwargs) if hasattr(func, '__call__') and hasattr(func, '__code__') else func(*args, **kwargs)
            
            # Guardar en cache
            if redis_client:
                try:
                    # Convertir a dict si es un modelo Pydantic
                    if hasattr(result, 'model_dump'):
                        result_dict = result.model_dump()
                    elif hasattr(result, 'dict'):
                        result_dict = result.dict()
                    else:
                        result_dict = result
                    
                    redis_client.setex(
                        cache_key,
                        ttl,
                        json.dumps(result_dict, default=str)
                    )
                    logger.debug(f"Cache guardado: {cache_key}")
                except Exception as e:
                    logger.warning(f"Error guardando en cache: {e}")
            
            return result
        return wrapper
    return decorator


def get_cached_statement(key: str) -> Optional[Any]:
    """
    Obtiene un statement del cache.
    
    Args:
        key: Clave de cache (ej: "student:1:statement")
    
    Returns:
        Datos cacheados o None si no existe
    """
    redis_client = get_redis_client()
    if not redis_client:
        return None
    
    try:
        cached = redis_client.get(key)
        if cached:
            logger.debug(f"Cache hit: {key}")
            return json.loads(cached)
    except Exception as e:
        logger.warning(f"Error leyendo cache: {e}")
    
    return None


def set_cached_statement(key: str, value: Any, ttl: int = 60):
    """
    Guarda un statement en el cache.
    
    Args:
        key: Clave de cache
        value: Valor a guardar
        ttl: Tiempo de vida en segundos (default: 60)
    """
    redis_client = get_redis_client()
    if not redis_client:
        return
    
    try:
        # Convertir a dict si es un modelo Pydantic
        if hasattr(value, 'model_dump'):
            value_dict = value.model_dump()
        elif hasattr(value, 'dict'):
            value_dict = value.dict()
        else:
            value_dict = value
        
        redis_client.setex(
            key,
            ttl,
            json.dumps(value_dict, default=str)
        )
        logger.debug(f"Cache guardado: {key}")
    except Exception as e:
        logger.warning(f"Error guardando en cache: {e}")


def invalidate_student_statement(student_id: int):
    """
    Invalida el cache del statement de un estudiante.
    
    Args:
        student_id: ID del estudiante
    """
    key = f"student:{student_id}:statement"
    _invalidate_key(key)


def invalidate_school_statement(school_id: int):
    """
    Invalida el cache del statement de un colegio.
    
    Args:
        school_id: ID del colegio
    """
    key = f"school:{school_id}:statement"
    _invalidate_key(key)


def invalidate_statements_for_invoice(invoice_id: int, db):
    """
    Invalida los statements relacionados con una factura.
    Necesita acceso a la DB para obtener student_id y school_id.
    
    Args:
        invoice_id: ID de la factura
        db: Sesión de base de datos
    """
    from app.models.invoice import Invoice
    
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()
    if invoice:
        invalidate_student_statement(invoice.student_id)
        if invoice.student and invoice.student.school_id:
            invalidate_school_statement(invoice.student.school_id)


def invalidate_statements_for_payment(payment_id: int, db):
    """
    Invalida los statements relacionados con un pago.
    Necesita acceso a la DB para obtener invoice -> student -> school.
    
    Args:
        payment_id: ID del pago
        db: Sesión de base de datos
    """
    from app.models.payment import Payment
    
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment and payment.invoice:
        invalidate_student_statement(payment.invoice.student_id)
        if payment.invoice.student and payment.invoice.student.school_id:
            invalidate_school_statement(payment.invoice.student.school_id)


def _invalidate_key(key: str):
    """
    Invalida una clave de cache.
    
    Args:
        key: Clave a invalidar
    """
    redis_client = get_redis_client()
    if not redis_client:
        return
    
    try:
        redis_client.delete(key)
        logger.info(f"Cache invalidado: {key}")
    except Exception as e:
        logger.warning(f"Error invalidando cache: {e}")

