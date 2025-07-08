# Facturación Segura

Este es un proyecto en Django para gestión de facturación. Incluye funcionalidades para administración de clientes, facturas y reportes.

## Requisitos

- Python 3.10 o superior
- Git

## Instalación

Clona el repositorio:

```bash
git clone https://github.com/esmora2/facturacion_segura.git
cd facturacion_segura
```


Crea un entorno virtual llamado venv:

Windows:

```bash
python -m venv venv
venv\Scripts\activate

```

macOS / Linux:


```bash
python3 -m venv venv
source venv/bin/activate

```

Instala las dependencias:

```bash
pip install -r requirements.txt


```

Migraciones
Aplica las migraciones para preparar la base de datos:

```bash
python manage.py migrate

```

Superusuario
Crea un superusuario para acceder al panel de administración:

```bash
python manage.py createsuperuser


```

Servidor de desarrollo
Inicia el servidor:

```bash
python manage.py runserver



```

Accede en el navegador en http://127.0.0.1:8000.