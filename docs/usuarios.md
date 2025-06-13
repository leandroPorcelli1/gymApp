# Documentación de Endpoints de Usuarios

## 1. Obtener Usuario por ID (GET)
- **Método**: `GET`
- **URL**: `http://localhost:5000/usuarios/<id>`
- **Respuesta exitosa**: `200 OK`
  ```json
  {
    "id": 1,
    "nombre": "Nombre del Usuario",
    "email": "usuario@ejemplo.com",
    "rol": "usuario"
  }
  ```
- **Respuesta de error**: `404 Not Found`
  ```json
  {
    "error": "Usuario no encontrado"
  }
  ```

## 2. Eliminar Usuario (DELETE)
- **Método**: `DELETE`
- **URL**: `http://localhost:5000/usuarios/<id>`
- **Respuesta exitosa**: `200 OK`
  ```json
  {
    "mensaje": "Usuario eliminado exitosamente"
  }
  ```
- **Respuesta de error**: `404 Not Found`
  ```json
  {
    "error": "Usuario no encontrado"
  }
  ```

## 3. Crear Usuario (POST)
- **Método**: `POST`
- **URL**: `http://localhost:5000/usuarios`
- **Headers**:
  - `Content-Type: application/json`
- **Body** (raw JSON):
  ```json
  {
    "nombre": "Nuevo Usuario",
    "email": "nuevo@ejemplo.com",
    "password": "contraseña123",
    "fecha_nacimiento": "1990-01-01",
    "genero": "masculino"
  }
  ```
- **Respuesta exitosa**: `201 Created`
  ```json
  {
    "mensaje": "Usuario creado",
    "id": 1
  }
  ```
- **Respuesta de error**: `400 Bad Request`
  ```json
  {
    "error": "Error al crear el usuario",
    "detalle": "Mensaje de error específico"
  }
  ``` 