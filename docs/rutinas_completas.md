# Documentación de Endpoints de Rutinas Completas

## 1. Crear Rutina Completa (POST)
- **Método**: `POST`
- **URL**: `http://localhost:5000/rutinas/completas`
- **Headers**:
  - `Content-Type: application/json`
- **Body** (raw JSON):
  ```json
  {
    "nombre": "Nombre de la Rutina",
    "descripcion": "Descripción de la Rutina (opcional)",
    "usuarios_id": 1,
    "nivel_rutinas_id": 1,
    "ejercicios": [
      {
        "nombre": "Nombre del Ejercicio",
        "descripcion": "Descripción del Ejercicio (opcional)",
        "series": [
          {
            "repeticiones": 10,
            "peso_kg": 20.5
          },
          {
            "repeticiones": 12,
            "peso_kg": 22.5
          }
        ]
      },
      {
        "nombre": "Otro Ejercicio",
        "descripcion": "Descripción de Otro Ejercicio (opcional)",
        "series": [
          {
            "repeticiones": 8,
            "peso_kg": 15.0
          }
        ]
      }
    ]
  }
  ```
- **Respuesta exitosa**: `201 Created`
  ```json
  {
    "mensaje": "Rutina completa creada exitosamente",
    "rutina": {
      "id": 1,
      "nombre": "Nombre de la Rutina",
      "descripcion": "Descripción de la Rutina",
      "ejercicios": [
        {
          "id": 1,
          "nombre": "Nombre del Ejercicio",
          "descripcion": "Descripción del Ejercicio",
          "series": [
            {
              "id": 1,
              "repeticiones": 10,
              "peso_kg": 20.5
            },
            {
              "id": 2,
              "repeticiones": 12,
              "peso_kg": 22.5
            }
          ]
        },
        {
          "id": 2,
          "nombre": "Otro Ejercicio",
          "descripcion": "Descripción de Otro Ejercicio",
          "series": [
            {
              "id": 3,
              "repeticiones": 8,
              "peso_kg": 15.0
            }
          ]
        }
      ]
    }
  }
  ```
- **Respuesta de error**: `400 Bad Request`
  ```json
  {
    "error": "Error al crear la rutina completa",
    "detalle": "Mensaje de error específico"
  }
  ```

## 2. Obtener Rutina Completa (GET)
- **Método**: `GET`
- **URL**: `http://localhost:5000/rutinas/completas/<id>`
- **Respuesta exitosa**: `200 OK`
  ```json
  {
    "id": 1,
    "nombre": "Nombre de la Rutina",
    "descripcion": "Descripción de la Rutina",
    "usuarios_id": 1,
    "nivel_rutinas_id": 1,
    "ejercicios": [
      {
        "id": 1,
        "nombre": "Nombre del Ejercicio",
        "descripcion": "Descripción del Ejercicio",
        "series": [
          {
            "id": 1,
            "repeticiones": 10,
            "peso_kg": 20.5
          },
          {
            "id": 2,
            "repeticiones": 12,
            "peso_kg": 22.5
          }
        ]
      },
      {
        "id": 2,
        "nombre": "Otro Ejercicio",
        "descripcion": "Descripción de Otro Ejercicio",
        "series": [
          {
            "id": 3,
            "repeticiones": 8,
            "peso_kg": 15.0
          }
        ]
      }
    ]
  }
  ```
- **Respuesta de error**: `400 Bad Request`
  ```json
  {
    "error": "Error al obtener la rutina completa",
    "detalle": "Mensaje de error específico"
  }
  ```

## 3. Eliminar Rutina Completa (DELETE)
- **Método**: `DELETE`
- **URL**: `http://localhost:5000/rutinas/completas/<id>`
- **Respuesta exitosa**: `200 OK`
  ```json
  {
    "mensaje": "Rutina completa eliminada exitosamente"
  }
  ```
- **Respuesta de error**: `400 Bad Request`
  ```json
  {
    "error": "Error al eliminar la rutina completa",
    "detalle": "Mensaje de error específico"
  }
  ```

## 4. Obtener Todas las Rutinas Completas (GET)
- **Método**: `GET`
- **URL**: `http://localhost:5000/rutinas/completas`
- **Respuesta exitosa**: `200 OK`
  ```json
  [
    {
      "id": 1,
      "nombre": "Nombre de la Rutina 1",
      "descripcion": "Descripción de la Rutina 1",
      "usuarios_id": 1,
      "nivel_rutinas_id": 1,
      "ejercicios": [
        {
          "id": 1,
          "nombre": "Nombre del Ejercicio 1",
          "descripcion": "Descripción del Ejercicio 1",
          "series": [
            {
              "id": 1,
              "repeticiones": 10,
              "peso_kg": 20.5
            },
            {
              "id": 2,
              "repeticiones": 12,
              "peso_kg": 22.5
            }
          ]
        }
      ]
    },
    {
      "id": 2,
      "nombre": "Nombre de la Rutina 2",
      "descripcion": "Descripción de la Rutina 2",
      "usuarios_id": 2,
      "nivel_rutinas_id": 2,
      "ejercicios": [
        {
          "id": 3,
          "nombre": "Nombre del Ejercicio 2",
          "descripcion": "Descripción del Ejercicio 2",
          "series": [
            {
              "id": 4,
              "repeticiones": 8,
              "peso_kg": 15.0
            }
          ]
        }
      ]
    }
  ]
  ```
- **Respuesta de error**: `400 Bad Request`
  ```json
  {
    "error": "Error al obtener las rutinas completas",
    "detalle": "Mensaje de error específico"
  }
  ``` 