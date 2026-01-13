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
- ✅ Sistema de pagos con actualización automática de estados
- ✅ Cálculo de estados de cuenta (colegio y estudiante)
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
docker-compose up -d
```

Esto levantará:
- PostgreSQL en el puerto 5432
- Redis en el puerto 6379
- Backend FastAPI en el puerto 8000

4. **Verificar que los servicios estén corriendo**:
```bash
docker-compose ps
```

5. **Acceder a la documentación de la API**:
Abre tu navegador en: http://localhost:8000/docs

## 🎯 Uso

### Endpoints Principales

#### Schools
- `POST /api/v1/schools/` - Crear colegio
- `GET /api/v1/schools/` - Listar colegios (con paginación)
- `GET /api/v1/schools/{id}` - Obtener colegio por ID
- `PUT /api/v1/schools/{id}` - Actualizar colegio
- `DELETE /api/v1/schools/{id}` - Eliminar colegio
- `GET /api/v1/schools/{id}/students/count` - Contar estudiantes

#### Students
- `POST /api/v1/students/` - Crear estudiante
- `GET /api/v1/students/` - Listar estudiantes (con paginación y filtros)
- `GET /api/v1/students/{id}` - Obtener estudiante por ID
- `PUT /api/v1/students/{id}` - Actualizar estudiante
- `DELETE /api/v1/students/{id}` - Eliminar estudiante

#### Invoices
- `POST /api/v1/invoices/` - Crear factura
- `GET /api/v1/invoices/` - Listar facturas (con paginación y filtros)
- `GET /api/v1/invoices/{id}` - Obtener factura por ID
- `PUT /api/v1/invoices/{id}` - Actualizar factura
- `DELETE /api/v1/invoices/{id}` - Eliminar factura
- `POST /api/v1/invoices/{id}/payments` - Crear pago para una factura

#### Accounts
- `GET /api/v1/accounts/schools/{id}` - Estado de cuenta del colegio
- `GET /api/v1/accounts/students/{id}` - Estado de cuenta del estudiante
- `GET /api/v1/accounts/students/{student_id}/debt/{school_id}` - Deuda de estudiante
- `GET /api/v1/accounts/schools/{id}/total-debt` - Deuda total del colegio

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
    "school_id": 1,
    "is_active": true
  }'
```

#### Crear una Factura
```bash
curl -X POST "http://localhost:8000/api/v1/invoices/" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "INV-2024-001",
    "student_id": 1,
    "amount": 1000.00,
    "description": "Mensualidad Enero 2024",
    "due_date": "2024-02-15T00:00:00",
    "status": "pending"
  }'
```

#### Registrar un Pago
```bash
curl -X POST "http://localhost:8000/api/v1/invoices/1/payments" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_id": 1,
    "amount": 500.00,
    "payment_method": "transfer",
    "payment_reference": "TRF-001",
    "notes": "Pago parcial"
  }'
```

#### Consultar Estado de Cuenta de un Estudiante
```bash
curl "http://localhost:8000/api/v1/accounts/students/1"
```

#### Consultar Estado de Cuenta de un Colegio
```bash
curl "http://localhost:8000/api/v1/accounts/schools/1"
```

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

Para cargar datos de ejemplo en la base de datos, puedes usar el script:

```bash
python scripts/load_sample_data.py
```

O ejecutarlo dentro del contenedor:

```bash
docker-compose exec backend python scripts/load_sample_data.py
```

## 🏗️ Estructura del Proyecto

```
mattilda/
├── app/
│   ├── api/
│   │   └── routes/
│   │       ├── schools.py      # Rutas de colegios
│   │       ├── students.py      # Rutas de estudiantes
│   │       ├── invoices.py      # Rutas de facturas
│   │       └── accounts.py      # Rutas de estados de cuenta
│   ├── core/
│   │   ├── config.py           # Configuración
│   │   └── database.py         # Configuración de BD
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
- `REDIS_URL`: URL de conexión a Redis (opcional)
- `ENVIRONMENT`: Entorno (development, production)
- `LOG_LEVEL`: Nivel de logging (INFO, DEBUG, etc.)

### Paginación

Los endpoints de listado soportan paginación con los parámetros:
- `skip`: Número de registros a saltar (default: 0)
- `limit`: Número de registros a retornar (default: 10, max: 100)

## 📝 Preguntas que Responde el Sistema

✅ **¿Cuánto le debe un estudiante a un colegio?**
- Endpoint: `GET /api/v1/accounts/students/{student_id}/debt/{school_id}`

✅ **¿Cuánto le deben todos los estudiantes a un colegio?**
- Endpoint: `GET /api/v1/accounts/schools/{school_id}/total-debt`

✅ **¿Cuántos alumnos tiene un colegio?**
- Endpoint: `GET /api/v1/schools/{school_id}/students/count`

✅ **¿Cuál es el estado de cuenta de un colegio o de un estudiante?**
- Endpoint: `GET /api/v1/accounts/schools/{school_id}`
- Endpoint: `GET /api/v1/accounts/students/{student_id}`

## 🐳 Comandos Docker

```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v

# Reconstruir imágenes
docker-compose build --no-cache

# Ejecutar comandos en el contenedor
docker-compose exec backend bash
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
- **School**: Representa un colegio con información básica
- **Student**: Estudiante asociado a un colegio (relación many-to-one)
- **Invoice**: Factura asociada a un estudiante (relación many-to-one)
- **Payment**: Pago asociado a una factura (relación many-to-one)

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

## 🤝 Contribuciones

Este es un proyecto de prueba técnica. Para mejoras o sugerencias, por favor abre un issue.

## 📄 Licencia

Este proyecto es de uso interno para evaluación técnica.

---

**Desarrollado con ❤️ para Mattilda**

