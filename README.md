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
- **Redis**: Cache
- **Pydantic**: Validación de datos
- **Docker & Docker Compose**: Contenedores

## 🚀 Inicio Rápido

### Requisitos Previos

- Docker y Docker Compose instalados
- Git (opcional)

### 1. Levantar el Proyecto con Docker

```bash
# Clonar el repositorio (si aplica)
git clone https://github.com/lbritosm/mattilda-challenge.git
cd mattilda-challenge

# Levantar todos los servicios
docker compose up -d
```

Esto levantará:
- PostgreSQL en el puerto 5432
- Redis en el puerto 6379
- Backend FastAPI en el puerto 8000

**Nota importante**: Al iniciar la aplicación, se ejecutan automáticamente las migraciones de Alembic. Esto asegura que la base de datos esté siempre actualizada con el esquema más reciente.

### 2. Verificar que los Servicios Estén Corriendo

```bash
docker compose ps
```

Todos los servicios deben mostrar estado "healthy" o "running".

### 3. Cargar Datos de Ejemplo

Para cargar datos de ejemplo en la base de datos (con personajes de Los Simpsons):

```bash
docker compose exec backend python scripts/load_sample_data.py
```

El script crea:
- 2 colegios (Escuela Primaria de Springfield e Instituto Springfield)
- 5 estudiantes (Bart, Lisa, Milhouse, Nelson y Martin)
- 6 facturas de ejemplo
- 3 pagos de ejemplo

### 4. Acceder a la API

- **Documentación Swagger**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **API Base**: http://localhost:8000/api/v1

### 5. Importar Colección de Postman

El proyecto incluye una colección completa de Postman con todos los endpoints listos para usar:

1. Abre Postman
2. Haz clic en **Import**
3. Selecciona los archivos:
   - `Mattilda_API.postman_collection.json`
   - `Mattilda_API.postman_environment.json`
4. Selecciona el entorno "Mattilda API - Local"

Para más detalles, consulta [POSTMAN_README.md](POSTMAN_README.md)

## 📦 Instalación Detallada

### Configurar Variables de Entorno (Opcional)

```bash
cp .env.example .env
# Editar .env si es necesario
```

Las variables de entorno disponibles están documentadas en la sección [Configuración](#-configuración).

## 🎯 Uso

### Endpoints Principales

#### Schools
- `POST /api/v1/schools/` - Crear colegio
- `GET /api/v1/schools/` - Listar colegios (con paginación y filtros)
  - **Filtros opcionales:**
    - `is_active` (bool): Filtrar por estado activo/inactivo
  - **Parámetros de paginación:**
    - `skip` (int, default: 0): Número de registros a saltar
    - `limit` (int, default: 10, max: 100): Número de registros a retornar
- `GET /api/v1/schools/{school_id}` - Obtener colegio por UUID
- `PUT /api/v1/schools/{school_id}` - Actualizar colegio
- `DELETE /api/v1/schools/{school_id}` - Eliminar colegio
- `GET /api/v1/schools/{school_id}/statement` - Estado de cuenta del colegio (con cache y paginación)
  - **Parámetros de paginación:**
    - `skip` (int, default: 0): Número de facturas a saltar
    - `limit` (int, default: 10, max: 100): Número de facturas a retornar

#### Students
- `POST /api/v1/students/` - Crear estudiante
- `GET /api/v1/students/` - Listar estudiantes (con paginación y filtros)
  - **Filtros opcionales:**
    - `school_id` (UUID): Filtrar por ID de colegio
    - `is_active` (bool): Filtrar por estado activo/inactivo
  - **Parámetros de paginación:**
    - `skip` (int, default: 0): Número de registros a saltar
    - `limit` (int, default: 10, max: 100): Número de registros a retornar
- `GET /api/v1/students/{student_id}` - Obtener estudiante por UUID
- `PUT /api/v1/students/{student_id}` - Actualizar estudiante
- `DELETE /api/v1/students/{student_id}` - Eliminar estudiante
- `GET /api/v1/students/{student_id}/statement` - Estado de cuenta del estudiante (con cache y paginación)
  - **Parámetros de paginación:**
    - `skip` (int, default: 0): Número de facturas a saltar
    - `limit` (int, default: 10, max: 100): Número de facturas a retornar

#### Invoices
- `POST /api/v1/invoices/` - Crear factura
- `GET /api/v1/invoices/` - Listar facturas (con paginación y filtros)
  - **Filtros opcionales:**
    - `student_id` (UUID): Filtrar por ID de estudiante
    - `school_id` (UUID): Filtrar por ID de colegio (facturas de estudiantes del colegio)
    - `status` (string): Filtrar por estado de factura
      - Valores posibles: `pending`, `paid`, `partial`, `cancelled`
  - **Parámetros de paginación:**
    - `skip` (int, default: 0): Número de registros a saltar
    - `limit` (int, default: 10, max: 100): Número de registros a retornar
- `GET /api/v1/invoices/{invoice_id}` - Obtener factura por UUID (incluye lista de pagos)
- `PUT /api/v1/invoices/{invoice_id}` - Actualizar factura
- `DELETE /api/v1/invoices/{invoice_id}` - Eliminar factura
- `GET /api/v1/invoices/{invoice_id}/payments` - Listar pagos de una factura (con paginación)
  - **Parámetros de paginación:**
    - `skip` (int, default: 0): Número de pagos a saltar
    - `limit` (int, default: 10, max: 100): Número de pagos a retornar
- `POST /api/v1/invoices/{invoice_id}/payments` - Crear pago para una factura

**Nota**: Todos los parámetros `{id}` en las rutas son UUIDs, no enteros.


#### Health & Metrics
- `GET /health` - Health check
- `GET /metrics` - Métricas básicas
- `GET /docs` - Documentación Swagger

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

#### Listar Colegios (con paginación y filtros)
```bash
# Primera página (10 colegios por defecto)
curl "http://localhost:8000/api/v1/schools/"

# Segunda página con 20 colegios
curl "http://localhost:8000/api/v1/schools/?skip=10&limit=20"

# Filtrar solo colegios activos
curl "http://localhost:8000/api/v1/schools/?is_active=true"

# Filtrar solo colegios inactivos
curl "http://localhost:8000/api/v1/schools/?is_active=false"

# Combinar filtros y paginación
curl "http://localhost:8000/api/v1/schools/?is_active=true&skip=0&limit=50"
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

#### Listar Estudiantes (con paginación y filtros)
```bash
# Primera página (10 estudiantes por defecto)
curl "http://localhost:8000/api/v1/students/"

# Filtrar por colegio
curl "http://localhost:8000/api/v1/students/?school_id=2c72f491-5084-4df9-be3a-dfa99bb16489"

# Filtrar solo estudiantes activos
curl "http://localhost:8000/api/v1/students/?is_active=true"

# Combinar filtros: estudiantes activos de un colegio específico
curl "http://localhost:8000/api/v1/students/?school_id=2c72f491-5084-4df9-be3a-dfa99bb16489&is_active=true"

# Con paginación personalizada
curl "http://localhost:8000/api/v1/students/?school_id=2c72f491-5084-4df9-be3a-dfa99bb16489&skip=0&limit=20"
```

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

#### Listar Facturas (con paginación y filtros)
```bash
# Primera página (10 facturas por defecto)
curl "http://localhost:8000/api/v1/invoices/"

# Filtrar por estudiante
curl "http://localhost:8000/api/v1/invoices/?student_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890"

# Filtrar por colegio (todas las facturas de estudiantes del colegio)
curl "http://localhost:8000/api/v1/invoices/?school_id=2c72f491-5084-4df9-be3a-dfa99bb16489"

# Filtrar por estado
curl "http://localhost:8000/api/v1/invoices/?status=pending"
# Estados disponibles: pending, paid, partial, cancelled

# Combinar múltiples filtros
curl "http://localhost:8000/api/v1/invoices/?school_id=2c72f491-5084-4df9-be3a-dfa99bb16489&status=pending"

# Con paginación personalizada
curl "http://localhost:8000/api/v1/invoices/?status=pending&skip=0&limit=20"

# Ejemplo completo: facturas pendientes de un estudiante específico, segunda página
curl "http://localhost:8000/api/v1/invoices/?student_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890&status=pending&skip=10&limit=10"
```

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

#### Listar Pagos de una Factura
```bash
# Primera página (10 pagos por defecto)
curl "http://localhost:8000/api/v1/invoices/a1b2c3d4-e5f6-7890-abcd-ef1234567890/payments"

# Con paginación personalizada
curl "http://localhost:8000/api/v1/invoices/a1b2c3d4-e5f6-7890-abcd-ef1234567890/payments?skip=0&limit=20"
```

**Nota**: Reemplaza `a1b2c3d4-e5f6-7890-abcd-ef1234567890` con el UUID real de la factura.

#### Consultar Estado de Cuenta de un Estudiante
```bash
# Primera página (10 facturas por defecto)
curl "http://localhost:8000/api/v1/students/a1b2c3d4-e5f6-7890-abcd-ef1234567890/statement"

# Con paginación personalizada
curl "http://localhost:8000/api/v1/students/a1b2c3d4-e5f6-7890-abcd-ef1234567890/statement?skip=0&limit=20"
```

#### Consultar Estado de Cuenta de un Colegio
```bash
# Primera página (10 facturas por defecto)
curl "http://localhost:8000/api/v1/schools/2c72f491-5084-4df9-be3a-dfa99bb16489/statement"

# Con paginación personalizada
curl "http://localhost:8000/api/v1/schools/2c72f491-5084-4df9-be3a-dfa99bb16489/statement?skip=10&limit=50"
```

**Nota**: 
- Reemplaza los UUIDs de ejemplo con los UUIDs reales obtenidos al crear los recursos.
- Los endpoints de statement soportan paginación con parámetros `skip` y `limit` (máximo 100 facturas por página).
- La respuesta incluye `total_invoices` para saber cuántas facturas hay en total.

## 🧪 Pruebas

### Ejecutar Pruebas en Docker (Recomendado)

**Nota**: Las pruebas se ejecutan dentro del contenedor Docker, que ya tiene configurada la conexión a la base de datos de pruebas.

```bash
# Ejecutar todas las pruebas
docker compose exec backend pytest

# Ejecutar con salida detallada (verbose)
docker compose exec backend pytest -v

# Ejecutar con cobertura (requiere pytest-cov)
docker compose exec backend pytest --cov=app tests/

# Nota: Si obtienes un error sobre --cov, reconstruye el contenedor:
# docker compose build backend
# docker compose up -d

# Ejecutar pruebas específicas
docker compose exec backend pytest tests/test_schools.py
docker compose exec backend pytest tests/test_students.py
docker compose exec backend pytest tests/test_invoices.py
docker compose exec backend pytest tests/test_accounts.py

# Ejecutar un test específico
docker compose exec backend pytest tests/test_schools.py::test_create_school -v

# Ejecutar con salida de errores detallada
docker compose exec backend pytest --tb=long

# Ver solo los tests que fallan
docker compose exec backend pytest --lf
```

**Configuración automática**:
- La base de datos de pruebas (`mattilda_test_db`) se crea automáticamente si no existe
- Cada test tiene su propia base de datos limpia (se recrea antes de cada test)
- No necesitas configurar nada manualmente

### Ejecutar Pruebas Localmente (sin Docker)

Si prefieres ejecutar las pruebas localmente:

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt

# Asegúrate de tener PostgreSQL corriendo y configurar DATABASE_URL
export DATABASE_URL="postgresql://mattilda:mattilda123@localhost:5432/mattilda_test_db"

# Ejecutar todas las pruebas
pytest

# Ejecutar con cobertura
pytest --cov=app tests/

# Ejecutar pruebas específicas
pytest tests/test_schools.py
```

**Nota**: Si ejecutas las pruebas localmente, necesitas tener PostgreSQL corriendo y ajustar la configuración en `tests/conftest.py` si es necesario.

### Estructura de Pruebas

- `tests/test_schools.py` - Pruebas de CRUD de colegios (6 tests)
- `tests/test_students.py` - Pruebas de CRUD de estudiantes y validación de deuda (5 tests)
- `tests/test_invoices.py` - Pruebas de facturas, pagos y paginación (5 tests)
- `tests/test_accounts.py` - Pruebas de estados de cuenta (2 tests)

**Total**: 18 pruebas de integración que cubren todos los endpoints y reglas de negocio.

## 📊 Modelo de Base de Datos

El sistema utiliza un modelo relacional con 4 entidades principales:

- **SCHOOLS** (Colegios): Información de instituciones educativas
- **STUDENTS** (Estudiantes): Estudiantes asociados a colegios
- **INVOICES** (Facturas): Facturas de estudiantes
- **PAYMENTS** (Pagos): Pagos realizados sobre facturas

### Relaciones
- Un colegio puede tener muchos estudiantes (1:N)
- Un estudiante puede tener muchas facturas (1:N)
- Una factura puede tener muchos pagos (1:N)

### Diagrama ER

```mermaid
erDiagram
    SCHOOLS {
        uuid id PK
        string name
        string address
        string phone
        string email
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    STUDENTS {
        uuid id PK
        string first_name
        string last_name
        string email
        date date_of_birth
        string student_code
        uuid school_id FK
        boolean is_active
        timestamp created_at
        timestamp updated_at
    }
    
    INVOICES {
        uuid id PK
        string invoice_number
        uuid school_id FK
        uuid student_id FK
        numeric total_amount
        string description
        date issue_date
        date due_date
        enum status
        timestamp created_at
        timestamp updated_at
    }
    
    PAYMENTS {
        uuid id PK
        uuid invoice_id FK
        uuid school_id FK
        uuid student_id FK
        numeric amount
        string payment_method
        string payment_reference
        string notes
        timestamp payment_date
        timestamp created_at
    }
    
    SCHOOLS ||--o{ STUDENTS : "tiene"
    SCHOOLS ||--o{ INVOICES : "tiene (denormalizado)"
    SCHOOLS ||--o{ PAYMENTS : "tiene (denormalizado)"
    STUDENTS ||--o{ INVOICES : "tiene"
    STUDENTS ||--o{ PAYMENTS : "tiene (denormalizado)"
    INVOICES ||--o{ PAYMENTS : "tiene"
```

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
│   │   ├── account.py          # Schemas de estados de cuenta
│   │   └── pagination.py       # Schema genérico de paginación
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

### Migraciones de Base de Datos

**Las migraciones se ejecutan automáticamente** cuando la aplicación se inicia. El sistema utiliza Alembic para gestionar las migraciones de la base de datos.

- **Ejecución automática**: Al iniciar la aplicación (evento `startup`), se intentan ejecutar automáticamente todas las migraciones pendientes usando `alembic upgrade head`
- **Fallback**: Si por alguna razón no se pueden ejecutar las migraciones de Alembic (por ejemplo, si Alembic no está disponible), el sistema usa `create_all()` como fallback (solo para desarrollo)
- **Migraciones manuales**: Si necesitas ejecutar migraciones manualmente:
  ```bash
  # Dentro del contenedor
  docker compose exec backend alembic upgrade head
  
  # O localmente (si tienes Alembic instalado)
  alembic upgrade head
  ```
- **Crear nuevas migraciones**:
  ```bash
  # Dentro del contenedor
  docker compose exec backend alembic revision --autogenerate -m "descripción de la migración"
  
  # O localmente
  alembic revision --autogenerate -m "descripción de la migración"
  ```

**Nota**: Si el contenedor no tiene Alembic instalado correctamente, puedes instalarlo manualmente:
```bash
docker compose exec backend pip install alembic==1.12.1
docker compose restart backend
```

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

### Paginación y Filtros

Todos los endpoints que retornan listas soportan paginación y filtros opcionales.

#### Parámetros de Paginación (comunes a todos los endpoints de listado)
- `skip` (int, default: 0): Número de registros a saltar
- `limit` (int, default: 10, max: 100): Número de registros a retornar

#### Filtros por Endpoint

**Schools (`GET /api/v1/schools/`):**
- `is_active` (bool, opcional): Filtrar por estado activo/inactivo
  - `true`: Solo colegios activos
  - `false`: Solo colegios inactivos
  - Sin parámetro: Todos los colegios

**Students (`GET /api/v1/students/`):**
- `school_id` (UUID, opcional): Filtrar por ID de colegio
- `is_active` (bool, opcional): Filtrar por estado activo/inactivo
  - `true`: Solo estudiantes activos
  - `false`: Solo estudiantes inactivos
  - Sin parámetro: Todos los estudiantes
- Los filtros se pueden combinar: `?school_id={uuid}&is_active=true`

**Invoices (`GET /api/v1/invoices/`):**
- `student_id` (UUID, opcional): Filtrar por ID de estudiante
- `school_id` (UUID, opcional): Filtrar por ID de colegio (retorna facturas de todos los estudiantes del colegio)
- `status` (string, opcional): Filtrar por estado de factura
  - Valores válidos: `pending`, `paid`, `partial`, `cancelled`
- Los filtros se pueden combinar: `?school_id={uuid}&status=pending`

**Statements:**
- `GET /api/v1/schools/{school_id}/statement`: Parámetros `skip` y `limit` para paginar facturas
- `GET /api/v1/students/{student_id}/statement`: Parámetros `skip` y `limit` para paginar facturas

**Payments:**
- `GET /api/v1/invoices/{invoice_id}/payments`: Parámetros `skip` y `limit` para paginar pagos

**Endpoints con paginación:**
- Listados: `/api/v1/schools/`, `/api/v1/students/`, `/api/v1/invoices/`
- Statements: `/api/v1/schools/{school_id}/statement`, `/api/v1/students/{student_id}/statement`

**Estructura de respuesta paginada:**
```json
{
  "items": [...],           // Lista de items de la página actual
  "total": 150,             // Total de items disponibles
  "skip": 0,                // Número de items saltados
  "limit": 10,              // Límite de items por página
  "has_next": true,         // Indica si hay más páginas
  "has_previous": false     // Indica si hay páginas anteriores
}
```

**Características:**
- Todos los listados están ordenados por fecha de creación descendente (más recientes primero)
- Los pagos están ordenados por fecha de pago descendente (más recientes primero)
- Los endpoints de statement calculan los totales (facturado, pagado, pendiente) usando **todas** las facturas, pero solo retornan la lista paginada de facturas
- La paginación permite manejar grandes volúmenes de datos eficientemente
- Los filtros se pueden combinar usando `&` en la URL
- Todos los filtros son opcionales; si no se especifican, se retornan todos los registros

## 📝 Preguntas que Responde el Sistema

✅ **¿Cuántos alumnos tiene un colegio?**
- Endpoint: `GET /api/v1/schools/{school_id}/statement`
- El campo `total_students` en la respuesta indica el número de estudiantes activos del colegio
- `school_id` debe ser un UUID válido

✅ **¿Cuál es el estado de cuenta de un colegio?**
- Endpoint: `GET /api/v1/schools/{school_id}/statement?skip=0&limit=10`
- `school_id` debe ser un UUID válido
- Parámetros opcionales: `skip` (default: 0), `limit` (default: 10, máximo: 100)
- Incluye: total facturado, total pagado, total pendiente, número de estudiantes y listado de facturas paginado
- La respuesta incluye `total_invoices` para conocer el total de facturas disponibles

✅ **¿Cuál es el estado de cuenta de un estudiante?**
- Endpoint: `GET /api/v1/students/{student_id}/statement?skip=0&limit=10`
- `student_id` debe ser un UUID válido
- Parámetros opcionales: `skip` (default: 0), `limit` (default: 10, máximo: 100)
- Incluye: total facturado, total pagado, total pendiente y listado de facturas paginado del estudiante
- La respuesta incluye `total_invoices` para conocer el total de facturas disponibles

## 🐳 Comandos Docker Útiles

```bash
# Ver logs
docker compose logs -f backend

# Detener servicios
docker compose down

# Detener y eliminar volúmenes (limpia la base de datos)
docker compose down -v

# Reconstruir imágenes
docker compose build --no-cache

# Ejecutar comandos en el contenedor
docker compose exec backend bash

# Verificar datos cargados
curl "http://localhost:8000/api/v1/schools/"
curl "http://localhost:8000/api/v1/students/"
curl "http://localhost:8000/api/v1/invoices/"
```

**Nota**: Si necesitas limpiar los datos y empezar de nuevo:

```bash
# Detener servicios y eliminar volúmenes
docker compose down -v

# Volver a levantar los servicios (creará una base de datos limpia)
docker compose up -d

# Cargar datos de ejemplo nuevamente
docker compose exec backend python scripts/load_sample_data.py
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

5. **Inicializar base de datos** (las migraciones se ejecutan automáticamente al iniciar la app):
```bash
# Opción 1: Ejecutar migraciones manualmente
alembic upgrade head

# Opción 2: Iniciar la app (ejecuta migraciones automáticamente)
uvicorn app.main:app --reload
```

6. **Ejecutar servidor**:
```bash
uvicorn app.main:app --reload
```

## 📚 Documentación Adicional

- **Swagger UI**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Métricas**: http://localhost:8000/metrics

## 🎨 Decisiones de Diseño

### Modelos de Datos
- **School**: Representa un colegio con información básica (ID: UUID)
- **Student**: Estudiante asociado a un colegio (relación many-to-one, IDs: UUID)
- **Invoice**: Factura asociada a un estudiante (relación many-to-one, IDs: UUID)
  - Incluye lista de pagos asociados (`payments`)
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

## 💼 Casos de Uso de Negocio y Decisiones Técnicas

Esta sección documenta las reglas de negocio implementadas y las decisiones técnicas clave que optimizan el rendimiento y garantizan la integridad de los datos.

### 🔒 Reglas de Negocio

#### 1. Inmutabilidad de `school_id` con Deuda Pendiente
**Regla**: Un estudiante no puede cambiar de colegio (`school_id`) si tiene deuda pendiente con su colegio actual.

**Implementación**:
- Al intentar actualizar el `school_id` de un estudiante, el sistema calcula la deuda total:
  - Deuda = Total Facturado - Total Pagado
- Si la deuda > 0, se rechaza la operación con error 400
- Si la deuda = 0, se permite el cambio del `school_id` del estudiante
- Al cambiar el `school_id`, se invalida el cache de statements de ambos colegios (anterior y nuevo) y del estudiante
- **Nota**: Las facturas y pagos existentes mantienen su `school_id` original. Solo se actualiza el `school_id` del estudiante.

**Endpoint afectado**: `PUT /api/v1/students/{student_id}`

**Ejemplo de error**:
```json
{
  "detail": "No se puede cambiar el colegio del estudiante. Tiene una deuda pendiente de $1000.00 con el colegio actual."
}
```

#### 2. Pagos Siempre Asociados a Facturas
**Regla**: Todos los pagos deben estar asociados a una factura. No se permiten "pagos a cuenta" sin factura.

**Implementación**:
- El campo `invoice_id` en la tabla `PAYMENTS` es **NOT NULL** (obligatorio)
- Al crear un pago, se valida que la factura exista
- El monto del pago no puede exceder el monto pendiente de la factura

**Endpoint afectado**: `POST /api/v1/invoices/{invoice_id}/payments`

#### 3. Derivación Automática de `school_id` y `student_id` en Pagos
**Regla**: Los campos `school_id` y `student_id` de un pago se obtienen automáticamente de la factura asociada. No se pueden enviar en el body de la petición.

**Implementación**:
- El schema `PaymentCreate` no incluye `school_id`, `student_id` ni `invoice_id`
- Estos campos se derivan automáticamente de la factura especificada en el path
- El sistema valida que los datos sean consistentes

**Endpoint afectado**: `POST /api/v1/invoices/{invoice_id}/payments`

**Ejemplo de request**:
```json
{
  "amount": "500.00",
  "payment_method": "transfer",
  "payment_reference": "TRF-001"
}
```

**Nota**: `school_id`, `student_id` e `invoice_id` se asignan automáticamente.

#### 4. Validación de Consistencia de `school_id` en Facturas
**Regla**: El `school_id` de una factura debe coincidir con el `school_id` del estudiante asociado.

**Implementación**:
- Al crear o actualizar una factura, se valida que `invoice.school_id == student.school_id`
- Si no coinciden, se rechaza la operación con error 400

**Endpoints afectados**: `POST /api/v1/invoices/`, `PUT /api/v1/invoices/{invoice_id}`

### ⚡ Optimizaciones Técnicas

#### 1. Denormalización de Base de Datos

**Decisión**: Se agregaron campos denormalizados para evitar joins costosos y mejorar el rendimiento de las consultas.

**Campos denormalizados**:

- **`INVOICES.school_id`**: 
  - **Razón**: Para calcular el estado de cuenta de un colegio, sin denormalización se necesitaría: `schools → students → invoices` (2 joins)
  - **Con denormalización**: Solo se consulta `invoices WHERE school_id = ?` (0 joins)
  - **Validación**: Se valida en la capa de servicio que `invoice.school_id == student.school_id`

- **`PAYMENTS.school_id` y `PAYMENTS.student_id`**:
  - **Razón**: Para calcular totales pagados por colegio o estudiante, sin denormalización se necesitaría: `payments → invoices → students → schools` (3 joins)
  - **Con denormalización**: Solo se consulta `payments WHERE school_id = ?` o `payments WHERE student_id = ?` (0 joins)
  - **Validación**: Estos campos se derivan automáticamente de la factura asociada

**Beneficios**:
- ✅ Consultas de estados de cuenta 3-4x más rápidas
- ✅ Evita doble conteo de pagos en agregaciones
- ✅ Queries más simples y mantenibles
- ✅ Mejor rendimiento con grandes volúmenes de datos

**Trade-offs**:
- ⚠️ Requiere mantener consistencia manual (validada en la capa de servicio)
- ⚠️ Más espacio en disco (mínimo impacto)

#### 2. Cache con Redis para Endpoints Pesados

**Decisión**: Implementar cache para endpoints que realizan agregaciones costosas (SUM, COUNT) y se consultan frecuentemente.

**Endpoints cacheados**:
- `GET /api/v1/students/{student_id}/statement`
- `GET /api/v1/schools/{school_id}/statement`

**Configuración**:
- **TTL (Time To Live)**: 60 segundos por defecto
- **Clave de cache**: Incluye `student_id`/`school_id`, `skip` y `limit` para soportar paginación
- **Invalidación automática**: El cache se invalida cuando:
  - Se crea, actualiza o elimina una factura (`POST/PUT/DELETE /api/v1/invoices/`)
  - Se crea un pago (`POST /api/v1/invoices/{invoice_id}/payments`)

**Implementación**:
- Invalidación por patrón: Se eliminan todas las versiones paginadas del statement
- Degradación elegante: Si Redis no está disponible, el sistema funciona normalmente sin cache

**Beneficios**:
- ✅ Respuestas instantáneas para consultas repetidas
- ✅ Reduce carga en la base de datos
- ✅ Mejora la experiencia del usuario en pantallas de "estado de cuenta"

#### 3. Índices Optimizados

**Decisión**: Crear índices específicos para las consultas más frecuentes.

**Índices implementados**:

**INVOICES**:
- `idx_invoice_school_due`: `(school_id, due_date DESC)` - Para estados de cuenta de colegios ordenados por vencimiento
- `idx_invoice_student_due`: `(student_id, due_date DESC)` - Para estados de cuenta de estudiantes ordenados por vencimiento
- `idx_invoice_school_status`: `(school_id, status)` - Para filtrar facturas por estado en un colegio
- `uq_invoice_school_number`: `UNIQUE(school_id, invoice_number)` - Garantiza unicidad de número de factura por colegio

**PAYMENTS**:
- `idx_payment_student_date`: `(student_id, payment_date DESC)` - Para listar pagos de un estudiante ordenados por fecha
- `idx_payment_school_date`: `(school_id, payment_date DESC)` - Para agregaciones de pagos por colegio
- `idx_payments_invoice_id`: `(invoice_id)` - Para listar pagos de una factura

**STUDENTS**:
- `idx_student_active_school`: `(school_id, is_active)` - Para contar estudiantes activos por colegio
- `uq_student_school_code`: `UNIQUE(school_id, student_code)` - Garantiza unicidad de código de estudiante por colegio

**Beneficios**:
- ✅ Consultas de estados de cuenta más rápidas
- ✅ Búsquedas y filtros optimizados
- ✅ Mejor rendimiento en operaciones de agregación

#### 4. Constraints de Integridad

**Decisión**: Implementar constraints a nivel de base de datos para garantizar la integridad de los datos.

**CHECK Constraints**:

- **INVOICES**:
  - `ck_invoice_total_amount_positive`: `total_amount >= 0` - Evita montos negativos
  - `ck_invoice_due_after_issue`: `due_date >= issue_date` - Evita fechas de vencimiento anteriores a la emisión

- **PAYMENTS**:
  - `ck_payment_amount_positive`: `amount > 0` - Garantiza que los pagos sean mayores a 0

**Unique Constraints**:
- `uq_invoice_school_number`: `UNIQUE(school_id, invoice_number)` - Número de factura único por colegio
- `uq_student_school_code`: `UNIQUE(school_id, student_code)` - Código de estudiante único por colegio

**Beneficios**:
- ✅ Integridad de datos garantizada a nivel de base de datos
- ✅ Previene errores de aplicación
- ✅ Validación en múltiples capas (aplicación + base de datos)

#### 5. Paginación en Todos los Endpoints de Listado

**Decisión**: Implementar paginación en todos los endpoints que retornan listas para manejar grandes volúmenes de datos.

**Endpoints con paginación**:
- `GET /api/v1/schools/`
- `GET /api/v1/students/`
- `GET /api/v1/invoices/`
- `GET /api/v1/invoices/{invoice_id}/payments`
- `GET /api/v1/schools/{school_id}/statement` (paginación de facturas dentro del statement)
- `GET /api/v1/students/{student_id}/statement` (paginación de facturas dentro del statement)

**Parámetros**:
- `skip` (default: 0): Número de registros a saltar
- `limit` (default: 10, máximo: 100): Número de registros a retornar

**Respuesta**:
```json
{
  "items": [...],
  "total": 150,
  "skip": 0,
  "limit": 10,
  "has_next": true,
  "has_previous": false
}
```

**Beneficios**:
- ✅ Manejo eficiente de grandes volúmenes de datos
- ✅ Mejor rendimiento (menos datos transferidos)
- ✅ Experiencia de usuario mejorada (carga más rápida)

#### 6. Actualización Inteligente del Estado de Facturas

**Decisión**: Optimizar cuándo se recalcula el estado de una factura para evitar cálculos innecesarios.

**Implementación**:
- **Al crear una factura**: No se actualiza el estado (siempre es `pending` inicialmente)
- **Al actualizar una factura**: Solo se recalcula el estado si cambió `total_amount`
- **Al crear un pago**: Siempre se recalcula el estado de la factura asociada

**Estados posibles**:
- `pending`: Total pagado = 0
- `partial`: 0 < Total pagado < Total facturado
- `paid`: Total pagado >= Total facturado

**Beneficios**:
- ✅ Menos operaciones innecesarias en la base de datos
- ✅ Mejor rendimiento en actualizaciones de facturas
- ✅ Estados siempre consistentes

### 📊 Resumen de Optimizaciones

| Optimización | Impacto | Beneficio |
|-------------|---------|-----------|
| Denormalización | Alto | Consultas 3-4x más rápidas, evita joins costosos |
| Cache Redis | Alto | Respuestas instantáneas en consultas repetidas |
| Índices optimizados | Medio | Búsquedas y filtros más rápidos |
| Constraints DB | Medio | Integridad garantizada a nivel de BD |
| Paginación | Alto | Manejo eficiente de grandes volúmenes |
| Actualización inteligente de estados | Bajo | Menos operaciones innecesarias |

## 🤝 Contribuciones

Este es un proyecto de prueba técnica. Para mejoras o sugerencias, por favor abre un issue.

## 📄 Licencia

Este proyecto es de uso interno para evaluación técnica.

---

**Desarrollado con ❤️ para Mattilda**

