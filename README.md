# DMS - Proyecto base (Django + PostgreSQL)

Proyecto base para la materia usando:

- Django (backend)
- PostgreSQL (base de datos)
- Docker Compose (para que todos lo levanten igual)

La idea es que cualquier integrante del grupo pueda ejecutarlo con pocos comandos, sin instalar Python ni PostgreSQL localmente.

## 1. Que debes instalar

Instala **Git** (para clonar el repositorio):

- [Git - descarga oficial](https://git-scm.com/downloads)

Instala **Docker Desktop** (ya incluye Docker y Docker Compose):

- [Docker Desktop - descarga oficial](https://www.docker.com/products/docker-desktop/)

Verifica en terminal:

```bash
git --version
docker --version
docker compose version
```

## 2. Clonar el repositorio

Clona el repositorio y entra a la carpeta del proyecto:

```bash
git clone <URL_DEL_REPOSITORIO>
cd NRC61057-aprende-y-mejora-unidad-3
```

## 3. Como lanzar el proyecto (primera vez)

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
docker compose up --build -d
```

Esto levanta:

- `web` (Django)
- `db` (PostgreSQL)

## 4. Ejecutar migraciones (obligatorio)

Despues de levantar los contenedores, ejecuta:

```bash
docker compose exec web python manage.py migrate
```

Este paso crea las tablas de Django y tambien crea un usuario admin de prueba (si no existe).

## 5. Accesos

- Aplicacion: <http://localhost:8000/>
- Healthcheck: <http://localhost:8000/health/>
- Admin Django: <http://localhost:8000/admin/>

## 6. Usuario admin de prueba

Se crea automaticamente al ejecutar `migrate`.

- Usuario: `admin`
- Password: `admin123`

## 7. Si aparece un error como `auth_user does not exist`

Significa que faltan migraciones.

Ejecuta:

```bash
docker compose exec web python manage.py migrate
```

## 8. Comandos utiles (opcionales)

Ver logs:

```bash
docker compose logs -f
```

Detener el proyecto:

```bash
docker compose down
```

## Nota breve

El archivo `/.env.dev` ya trae una configuracion compartida para el curso. No necesitas cambiarlo para empezar.
