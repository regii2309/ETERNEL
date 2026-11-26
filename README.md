
# Hacienda – Restaurante de Fusión Gastronómica

## Descripción del proyecto

Hacienda es un proyecto de desarrollo web enfocado en la creación de una plataforma digital para un restaurante que busca ofrecer una experiencia gastronómica única, combinando la esencia de una hacienda mexicana tradicional con la elegancia y sofisticación de la cultura europea.

El concepto del restaurante se basa en la fusión de tres identidades gastronómicas y culturales, integrando sabores, ingredientes, técnicas culinarias y estilos que dan vida a una propuesta diferente.

Nuestra propuesta busca transmitir la calidez de México, la elegancia europea y la riqueza de una experiencia gastronómica multicultural.

## Concepto del restaurante

El restaurante representa la unión de tres mundos:

- **México:** Tradición, ingredientes regionales, arquitectura de hacienda, colores cálidos y hospitalidad.
- **Europa:** Elegancia, sofisticación, técnicas culinarias y presentación de alta cocina.
- **Fusión gastronómica:** Una combinación de sabores, ingredientes y tradiciones que crean una experiencia culinaria original.
La identidad visual del restaurante busca reflejar un ambiente exclusivo, acogedor y elegante, inspirado en las antiguas haciendas mexicanas con detalles de estilo europeo.

## Objetivo del proyecto

Desarrollar un sistema web que permita representar digitalmente la identidad del restaurante y facilitar la interacción de los usuarios con sus servicios.

El proyecto busca integrar diseño, funcionalidad y tecnología para ofrecer una experiencia intuitiva y visualmente atractiva.

## Tecnologías utilizadas

- **Python:** Lenguaje principal de programación.
- **Flask:** Framework para el desarrollo de la aplicación web.
- **HTML5:** Estructura de las páginas web.
- **CSS3:** Diseño y estilos visuales.
- **JavaScript:** Interactividad del sitio web.
- **SQLite:** Gestión y almacenamiento de información.
- **Jinja2:** Motor de plantillas para Flask.

## Estructura del proyecto

```text
ETERNEL/
│
├── __pycache__/
│
├── Mi-Entorno/
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
├── templates/
│   ├── base.html
│   └── index.html
│
├── app.py
├── crear_db.py
├── database.db
├── requirement.txt
├── .gitignore
└── README.md
```

## Instalación y ejecución

### 1. Clonar el repositorio

```bash
git clone URL_DEL_REPOSITORIO
```

### 2. Entrar a la carpeta del proyecto

```bash
cd ETERNAL
```

### 3. Crear un entorno virtual

```bash
python -m venv Mi-Entorno
```

### 4. Activar el entorno virtual

En Windows:

```bash
Mi-Entorno\Scripts\activate
```

En Linux o macOS:

```bash
source Mi-Entorno/bin/activate
```

### 5. Instalar las dependencias

```bash
pip install -r requirement.txt
```

### 6. Crear la base de datos

```bash
python crear_db.py
```

### 7. Ejecutar el proyecto

```bash
python app.py
```

Después, abre tu navegador y visita:

```text
http://127.0.0.1:5000/
```

## Identidad y filosofía

Hacienda nace de la idea de reunir culturas alrededor de una misma mesa.

Un espacio donde la tradición mexicana se encuentra con la sofisticación europea y donde cada platillo representa una combinación de historia, creatividad y pasión por la gastronomía.

Más que un restaurante, buscamos representar una experiencia donde la arquitectura, los sabores y la hospitalidad se convierten en parte de una misma identidad.

## Estado del proyecto

En desarrollo.

## Autor

Proyecto desarrollado como parte de una iniciativa de desarrollo web y diseño de experiencias gastronómicas.
