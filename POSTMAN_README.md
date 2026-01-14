# Colección de Postman - Mattilda API

Esta carpeta contiene la colección de Postman para probar todos los endpoints de la API de Mattilda.

## 📦 Archivos

- **`Mattilda_API.postman_collection.json`**: Colección completa con todos los endpoints
- **`Mattilda_API.postman_environment.json`**: Variables de entorno para facilitar el uso

## 🚀 Cómo Importar en Postman

### Opción 1: Importar desde archivos

1. Abre Postman
2. Haz clic en **Import** (botón en la esquina superior izquierda)
3. Selecciona **File** o arrastra los archivos
4. Selecciona ambos archivos:
   - `Mattilda_API.postman_collection.json`
   - `Mattilda_API.postman_environment.json`
5. Haz clic en **Import**

### Opción 2: Importar desde URL (si está en un repositorio)

1. Abre Postman
2. Haz clic en **Import**
3. Selecciona **Link**
4. Pega la URL del archivo JSON de la colección
5. Haz clic en **Continue** y luego en **Import**

## ⚙️ Configuración

### Variables de Entorno

La colección incluye las siguientes variables:

- **`base_url`**: URL base de la API (por defecto: `http://localhost:8000`)
- **`school_id`**: UUID del colegio (se actualiza automáticamente)
- **`student_id`**: UUID del estudiante (se actualiza automáticamente)
- **`invoice_id`**: UUID de la factura (se actualiza automáticamente)

### Seleccionar el Entorno

1. En Postman, haz clic en el selector de entorno (esquina superior derecha)
2. Selecciona **"Mattilda API - Local"**

### Actualizar Variables Automáticamente

Para que los IDs se actualicen automáticamente después de crear recursos, puedes usar scripts de Postman. Sin embargo, la forma más simple es:

1. Crear un colegio → Copiar el `id` de la respuesta
2. Pegar el `id` en la variable `school_id` del entorno
3. Repetir para `student_id` e `invoice_id`

## 📋 Estructura de la Colección

La colección está organizada en carpetas:

### 1. Health & Info
- Health Check
- Metrics

### 2. Schools
- Create School
- List Schools (con paginación y filtros)
- Count Schools
- Get School by ID
- Update School
- Delete School
- Count School Students
- Get School Statement (con cache)

### 3. Students
- Create Student
- List Students (con paginación y filtros)
- Count Students
- Get Student by ID
- Update Student
- Delete Student
- Get Student Statement (con cache)

### 4. Invoices
- Create Invoice
- List Invoices (con paginación y filtros)
- Count Invoices
- Get Invoice by ID
- Update Invoice
- Delete Invoice
- List Invoice Payments
- Create Payment

## 🎯 Flujo de Trabajo Recomendado

1. **Iniciar servicios**:
   ```bash
   docker compose up -d
   ```

2. **Cargar datos de ejemplo** (opcional):
   ```bash
   docker compose exec backend python scripts/load_sample_data.py
   ```

3. **Verificar Health Check**:
   - Ejecutar "Health Check" en Postman

4. **Crear recursos en orden**:
   - Crear un School → Copiar `school_id` a la variable
   - Crear un Student → Copiar `student_id` a la variable
   - Crear una Invoice → Copiar `invoice_id` a la variable
   - Crear un Payment

5. **Probar endpoints de consulta**:
   - List Schools/Students/Invoices
   - Get Statements
   - Count endpoints

## 💡 Tips

- **Paginación**: Todos los endpoints de listado soportan `skip` y `limit`
- **Filtros**: Los endpoints de listado tienen filtros opcionales (ver query params)
- **Cache**: Los endpoints de statement (`/statement`) usan cache de Redis (TTL: 60s)
- **UUIDs**: Todos los IDs son UUIDs, no enteros
- **Validaciones**: Revisa las descripciones de cada request para ver reglas de negocio

## 🔧 Personalizar

### Cambiar la URL Base

1. Selecciona el entorno "Mattilda API - Local"
2. Edita la variable `base_url`
3. Por ejemplo, para producción: `https://api.mattilda.com`

### Agregar Tests Automáticos

Puedes agregar scripts de test en Postman para validar respuestas automáticamente. Por ejemplo:

```javascript
// En la pestaña "Tests" de un request
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

pm.test("Response has id", function () {
    var jsonData = pm.response.json();
    pm.expect(jsonData).to.have.property('id');
    
    // Guardar ID en variable si es necesario
    if (pm.request.url.path.includes('schools')) {
        pm.environment.set("school_id", jsonData.id);
    }
});
```

## 📚 Documentación Adicional

- **Swagger UI**: http://localhost:8000/docs
- **README Principal**: Ver `README.md` en la raíz del proyecto

