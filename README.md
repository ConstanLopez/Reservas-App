Para iniciar el proyecto:

Levantar el docker compose con los siguientes comandos, en la carpeta dond esta el compose con los siguientes comandos

# Build + up (usa el compose correcto)
docker compose -f "docker-compose reservAPP.yml" up -d --build

# Ver contenedores del stack
docker compose -f "docker-compose reservAPP.yml" ps

# Logs del backend (salida en vivo)
docker compose -f "docker-compose reservAPP.yml" logs -f backend

# Frontend
Para prender el frontend, navegar hasta la carpeta frontend y inicializar con :
npm run dev

# Backend
Para prender el backend se tiene que haber hecho la parte de docker previamente y  hacer:
python -m app.main

# Data Grip
Host: localhost
Port: 3307    
User: appuser
Password: apppass
Database: reservas_db
