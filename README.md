# Mattilda API

Sistema de gestión para colegios, estudiantes y facturación desarrollado con FastAPI y PostgreSQL.

## 📋 Descripción

Este proyecto implementa un sistema completo para la gestión de:
- **Colegios (Schools)**: Administración de instituciones educativas
- **Estudiantes (Students)**: Gestión de estudiantes asociados a colegios
- **Facturas (Invoices)**: Sistema de facturación y pagos
- **Estados de Cuenta**: Consultas de deudas y pagos

## 🚀 Características

- ✅ CRUD completo para Colegios, Estudiantes y Facturas
- ✅ IDs con UUID para mayor seguridad (evita enumeración)
- ✅ Sistema de pagos con actualización automática de estados
- ✅ Cálculo de estados de cuenta (colegio y estudiante)
- ✅ Cache con Redis para optimizar consultas pesadas (statements)
- ✅ Invalidación automática de cache cuando cambian datos financieros
- ✅ Paginación en todos los endpoints de listado
- ✅ Validación de datos con Pydantic
- ✅ Documentación automática (OpenAPI/Swagger)
- ✅ Health checks y métricas básicas
- ✅ Pruebas unitarias e integración
- ✅ Dockerizado con Docker Compose

## 🛠️ Tecnologías

- **Python 3.11**
- **FastAPI**: Framework web moderno y rápido
- **SQLAlchemy 2.0**: ORM para PostgreSQL
- **PostgreSQL 15**: Base de datos relacional
- **Redis**: Cache (opcional)
- **Pydantic**: Validación de datos
- **Docker & Docker Compose**: Contenedores

## 📦 Instalación

### Requisitos Previos

- Docker y Docker Compose instalados
- Git (opcional)

### Pasos de Instalación

1. **Clonar el repositorio** (si aplica):
```bash
git clone <repository-url>
cd mattilda
```

2. **Configurar variables de entorno** (opcional):
```bash
cp .env.example .env
# Editar .env si es necesario
```

3. **Levantar los servicios con Docker Compose**:
```bash
docker compose up -d
```

Esto levantará:
- PostgreSQL en el puerto 5432
- Redis en el puerto 6379
- Backend FastAPI en el puerto 8000

4. **Verificar que los servicios estén corriendo**:
```bash
docker compose ps
```

5. **Acceder a la documentación de la API**:
Abre tu navegador en: http://localhost:8000/docs

## 🎯 Uso

### Endpoints Principales

#### Schools
- `POST /api/v1/schools/` - Crear colegio
- `GET /api/v1/schools/` - Listar colegios (con paginación)
- `GET /api/v1/schools/{school_id}` - Obtener colegio por UUID
- `PUT /api/v1/schools/{school_id}` - Actualizar colegio
- `DELETE /api/v1/schools/{school_id}` - Eliminar colegio
- `GET /api/v1/schools/{school_id}/students/count` - Contar estudiantes
- `GET /api/v1/schools/{school_id}/statement` - Estado de cuenta del colegio (con cache)

#### Students
- `POST /api/v1/students/` - Crear estudiante
- `GET /api/v1/students/` - Listar estudiantes (con paginación y filtros)
- `GET /api/v1/students/{student_id}` - Obtener estudiante por UUID
- `PUT /api/v1/students/{student_id}` - Actualizar estudiante
- `DELETE /api/v1/students/{student_id}` - Eliminar estudiante
- `GET /api/v1/students/{student_id}/statement` - Estado de cuenta del estudiante (con cache)

#### Invoices
- `POST /api/v1/invoices/` - Crear factura
- `GET /api/v1/invoices/` - Listar facturas (con paginación y filtros)
- `GET /api/v1/invoices/{invoice_id}` - Obtener factura por UUID
- `PUT /api/v1/invoices/{invoice_id}` - Actualizar factura
- `DELETE /api/v1/invoices/{invoice_id}` - Eliminar factura
- `POST /api/v1/invoices/{invoice_id}/payments` - Crear pago para una factura

**Nota**: Todos los parámetros `{id}` en las rutas son UUIDs, no enteros.


#### Health & Metrics
- `GET /health` - Health check
- `GET /metrics` - Métricas básicas
- `GET /docs` - Documentación Swagger
- `GET /redoc` - Documentación ReDoc

### Ejemplos de Uso

#### Crear un Colegio
```bash
curl -X POST "http://localhost:8000/api/v1/schools/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Colegio San José",
    "address": "Calle Principal 123",
    "phone": "123456789",
    "email": "info@colegiosanjose.edu",
    "is_active": true
  }'
```

#### Crear un Estudiante
```bash
curl -X POST "http://localhost:8000/api/v1/students/" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Juan",
    "last_name": "Pérez",
    "email": "juan.perez@email.com",
    "school_id": "2c72f491-5084-4df9-be3a-dfa99bb16489",
    "is_active": true
  }'
```

**Nota**: `school_id` debe ser un UUID válido. Obtén el UUID del colegio desde la respuesta al crearlo o listando los colegios.

#### Crear una Factura
```bash
curl -X POST "http://localhost:8000/api/v1/invoices/" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "INV-2024-001",
    "student_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "amount": 1000.00,
    "description": "Mensualidad Enero 2024",
    "due_date": "2024-02-15T00:00:00",
    "status": "pending"
  }'
```

**Nota**: `student_id` debe ser un UUID válido del estudiante.

#### Registrar un Pago
```bash
curl -X POST "http://localhost:8000/api/v1/invoices/a1b2c3d4-e5f6-7890-abcd-ef1234567890/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    "amount": 500.00,
    "payment_method": "transfer",
    "payment_reference": "TRF-001",
    "notes": "Pago parcial"
  }'
```

**Nota**: Reemplaza `a1b2c3d4-e5f6-7890-abcd-ef1234567890` con el UUID real de la factura.

#### Consultar Estado de Cuenta de un Estudiante
```bash
curl "http://localhost:8000/api/v1/students/a1b2c3d4-e5f6-7890-abcd-ef1234567890/statement"
```

#### Consultar Estado de Cuenta de un Colegio
```bash
curl "http://localhost:8000/api/v1/schools/2c72f491-5084-4df9-be3a-dfa99bb16489/statement"
```

**Nota**: Reemplaza los UUIDs de ejemplo con los UUIDs reales obtenidos al crear los recursos.

## 🧪 Pruebas

### Ejecutar Pruebas

**Nota**: Para ejecutar las pruebas, necesitas tener PostgreSQL corriendo localmente o ajustar la configuración en `tests/conftest.py`.

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=app tests/

# Ejecutar pruebas específicas
pytest tests/test_schools.py
```

### Estructura de Pruebas

- `tests/test_schools.py` - Pruebas de CRUD de colegios
- `tests/test_students.py` - Pruebas de CRUD de estudiantes
- `tests/test_invoices.py` - Pruebas de facturas y pagos
- `tests/test_accounts.py` - Pruebas de estados de cuenta

## 📊 Cargar Datos de Ejemplo

Para cargar datos de ejemplo en la base de datos (con personajes de Los Simpsons), puedes usar el script:

```bash
python scripts/load_sample_data.py
```

O ejecutarlo dentro del contenedor:

```bash
docker compose exec backend python scripts/load_sample_data.py
```

El script crea:
- 2 colegios (Escuela Primaria de Springfield e Instituto Springfield)
- 5 estudiantes (Bart, Lisa, Milhouse, Nelson y Martin)
- 6 facturas de ejemplo
- 3 pagos de ejemplo

## 🏗️ Estructura del Proyecto

```
mattilda/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── schools.py      # Rutas de colegios
│   │       ├── students.py      # Rutas de estudiantes
│   │       └── invoices.py      # Rutas de facturas
│   ├── core/
│   │   ├── config.py           # Configuración
│   │   ├── database.py         # Configuración de BD
│   │   └── cache.py            # Cache con Redis
│   ├── models/
│   │   ├── school.py           # Modelo School
│   │   ├── student.py          # Modelo Student
│   │   ├── invoice.py          # Modelo Invoice
│   │   └── payment.py          # Modelo Payment
│   ├── schemas/
│   │   ├── school.py           # Schemas de School
│   │   ├── student.py          # Schemas de Student
│   │   ├── invoice.py          # Schemas de Invoice
│   │   ├── payment.py          # Schemas de Payment
│   │   └── account.py          # Schemas de Account
│   ├── services/
│   │   ├── school_service.py   # Lógica de negocio de colegios
│   │   ├── student_service.py  # Lógica de negocio de estudiantes
│   │   ├── invoice_service.py  # Lógica de negocio de facturas
│   │   └── account_service.py  # Lógica de estados de cuenta
│   └── main.py                 # Aplicación principal
├── tests/
│   ├── conftest.py            # Configuración de pytest
│   ├── test_schools.py        # Pruebas de colegios
│   ├── test_students.py       # Pruebas de estudiantes
│   ├── test_invoices.py       # Pruebas de facturas
│   └── test_accounts.py       # Pruebas de estados de cuenta
├── scripts/
│   └── load_sample_data.py    # Script para cargar datos de ejemplo
├── docker-compose.yml         # Configuración de Docker Compose
├── Dockerfile                 # Imagen del backend
├── requirements.txt           # Dependencias Python
└── README.md                  # Este archivo
```

## 🔧 Configuración

### Variables de Entorno

Puedes configurar las siguientes variables en el archivo `.env`:

- `DATABASE_URL`: URL de conexión a PostgreSQL
- `REDIS_URL`: URL de conexión a Redis (opcional, para cache)
- `ENVIRONMENT`: Entorno (development, production)
- `LOG_LEVEL`: Nivel de logging (INFO, DEBUG, etc.)

### Cache con Redis

El sistema utiliza Redis para cachear los endpoints de statements (estados de cuenta), que son consultas pesadas con agregaciones:

- **Endpoints cacheados**:
  - `GET /api/v1/students/{student_id}/statement`
  - `GET /api/v1/schools/{school_id}/statement`
  
  Los parámetros `{student_id}` y `{school_id}` deben ser UUIDs válidos.

- **TTL (Time To Live)**: 60 segundos por defecto

- **Invalidación automática**: El cache se invalida automáticamente cuando:
  - Se crea, actualiza o elimina una factura
  - Se crea un pago

- **Degradación elegante**: Si Redis no está disponible, el sistema funciona normalmente sin cache

### Paginación

Los endpoints de listado soportan paginación con los parámetros:
- `skip`: Número de registros a saltar (default: 0)
- `limit`: Número de registros a retornar (default: 10, max: 100)

## 📝 Preguntas que Responde el Sistema

✅ **¿Cuántos alumnos tiene un colegio?**
- Endpoint: `GET /api/v1/schools/{school_id}/students/count`
- `school_id` debe ser un UUID válido

✅ **¿Cuál es el estado de cuenta de un colegio?**
- Endpoint: `GET /api/v1/schools/{school_id}/statement`
- `school_id` debe ser un UUID válido
- Incluye: total facturado, total pagado, total pendiente, número de estudiantes y listado de facturas

✅ **¿Cuál es el estado de cuenta de un estudiante?**
- Endpoint: `GET /api/v1/students/{student_id}/statement`
- `student_id` debe ser un UUID válido
- Incluye: total facturado, total pagado, total pendiente y listado de facturas del estudiante

## 🐳 Comandos Docker

```bash
# Levantar todos los servicios
docker compose up -d

# Ver logs
docker compose logs -f backend

# Detener servicios
docker compose down

# Detener y eliminar volúmenes
docker compose down -v

# Reconstruir imágenes
docker compose build --no-cache

# Ejecutar comandos en el contenedor
docker compose exec backend bash
```

## 🔍 Desarrollo Local (sin Docker)

Si prefieres desarrollar sin Docker:

1. **Instalar PostgreSQL** y crear la base de datos:
```bash
createdb mattilda_db
```

2. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar variables de entorno**:
```bash
export DATABASE_URL="postgresql://user:password@localhost:5432/mattilda_db"
```

5. **Inicializar base de datos**:
```bash
python -c "from app.core.database import init_db; init_db()"
```

6. **Ejecutar servidor**:
```bash
uvicorn app.main:app --reload
```

## 📚 Documentación Adicional

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health
- **Métricas**: http://localhost:8000/metrics

## 🎨 Decisiones de Diseño

### Modelos de Datos
- **School**: Representa un colegio con información básica (ID: UUID)
- **Student**: Estudiante asociado a un colegio (relación many-to-one, IDs: UUID)
- **Invoice**: Factura asociada a un estudiante (relación many-to-one, IDs: UUID)
- **Payment**: Pago asociado a una factura (relación many-to-one, IDs: UUID)

### Identificadores (IDs)
- Todos los IDs utilizan **UUID v4** en lugar de enteros secuenciales
- **Ventajas**:
  - Mayor seguridad: evita la enumeración de recursos
  - Identificadores únicos globalmente
  - No revelan información sobre la cantidad de registros
- **Formato**: `xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx` (ej: `2c72f491-5084-4df9-be3a-dfa99bb16489`)

### Estados de Factura
- `pending`: Factura pendiente de pago
- `partial`: Factura con pago parcial
- `paid`: Factura pagada completamente
- `cancelled`: Factura cancelada

### Validaciones
- Validación de existencia de relaciones (estudiante en colegio, factura en estudiante)
- Validación de montos (no negativos, no exceder monto pendiente)
- Validación de unicidad (número de factura, código de estudiante)

### Lógica de Negocio
- Actualización automática del estado de factura al crear pagos
- Cálculo de deudas considerando pagos parciales
- Agregación de totales por colegio y estudiante
- Cache inteligente con invalidación automática para optimizar consultas pesadas

## 🤝 Contribuciones

Este es un proyecto de prueba técnica. Para mejoras o sugerencias, por favor abre un issue.

## 📄 Licencia

Este proyecto es de uso interno para evaluación técnica.

---

**Desarrollado con ❤️ para Mattilda**

