"""
Manejo personalizado de excepciones para mejorar los mensajes de error.
"""
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from typing import Any, Dict, List


def format_validation_error(error: Dict[str, Any]) -> str:
    """
    Formatea un error de validación en un mensaje legible en español.
    
    Args:
        error: Diccionario con la información del error de Pydantic
    
    Returns:
        Mensaje de error formateado en español
    """
    error_type = error.get("type", "")
    loc = error.get("loc", [])
    msg = error.get("msg", "")
    input_value = error.get("input")
    
    # Obtener el campo que causó el error (excluir 'body', 'query', 'path' que son metadatos)
    field_parts = [str(l) for l in loc if l not in ("body", "query", "path")]
    field_path = " -> ".join(field_parts) if field_parts else "parámetro"
    
    # Traducir tipos de error comunes
    ctx = error.get("ctx", {})
    
    error_messages = {
        "int_parsing": f"El valor '{input_value}' no es un número entero válido. Por favor, ingresa un número entero.",
        "uuid_parsing": f"El valor '{input_value}' no es un UUID válido. Por favor, ingresa un UUID en formato correcto (ej: 550e8400-e29b-41d4-a716-446655440000).",
        "string_type": f"Se esperaba texto, pero se recibió: {input_value}",
        "missing": f"El campo '{field_path}' es requerido y no puede estar vacío",
        "value_error": msg,
        "type_error": msg,
        "greater_than_equal": f"El valor debe ser mayor o igual a {ctx.get('ge', '')}",
        "less_than_equal": f"El valor debe ser menor o igual a {ctx.get('le', '')}",
        "string_too_short": f"El texto es demasiado corto. Mínimo {ctx.get('min_length', '')} caracteres requeridos",
        "string_too_long": f"El texto es demasiado largo. Máximo {ctx.get('max_length', '')} caracteres permitidos",
        "email": f"'{input_value}' no es un email válido. Por favor, ingresa un email con formato correcto (ej: usuario@dominio.com)",
        "url": f"'{input_value}' no es una URL válida",
    }
    
    # Mensaje personalizado según el tipo
    if error_type in error_messages:
        message = error_messages[error_type]
    else:
        # Mensaje genérico con el mensaje original
        message = f"{msg}"
        if input_value is not None and str(input_value).strip():
            message += f" (valor recibido: '{input_value}')"
    
    # Si hay un campo específico, agregarlo al mensaje
    if field_path and field_path != "parámetro":
        return f"Campo '{field_path}': {message}"
    
    return message


async def validation_exception_handler(
    request: Request, 
    exc: RequestValidationError
) -> JSONResponse:
    """
    Maneja excepciones de validación y retorna mensajes de error legibles.
    
    Args:
        request: Request de FastAPI
        exc: Excepción de validación
    
    Returns:
        JSONResponse con errores formateados
    """
    errors = []
    
    for error in exc.errors():
        loc = error.get("loc", [])
        field_parts = [str(l) for l in loc if l not in ("body", "query", "path")]
        field_name = " -> ".join(field_parts) if field_parts else "parámetro desconocido"
        
        formatted_error = {
            "campo": field_name,
            "mensaje": format_validation_error(error),
            "tipo": error.get("type", "unknown"),
            "ubicacion": list(loc),
        }
        errors.append(formatted_error)
    
    # Mensaje general
    if len(errors) == 1:
        general_message = f"Error de validación: {errors[0]['mensaje']}"
    else:
        general_message = f"Se encontraron {len(errors)} errores de validación"
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "Error de validación",
            "mensaje": general_message,
            "detalles": errors
        }
    )

