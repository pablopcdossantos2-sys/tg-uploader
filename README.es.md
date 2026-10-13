# TG Uploader

**Lea este README en otros idiomas:** [Português](README.md) · [English](README.en.md)

Aplicación de escritorio portátil para Windows, escrita en Python, destinada al envío de archivos desde una carpeta local a grupos de Telegram, con interfaz moderna, progreso real, historial, prevención de duplicados y recuperación de colas interrumpidas.

> Proyecto independiente y no oficial. TG Uploader utiliza la API de Telegram mediante Telethon y no está afiliado a Telegram.

## Funciones

- interfaz moderna con `CustomTkinter`;
- idiomas **Português (Brasil)**, **English** y **Español**;
- idioma seleccionado guardado entre ejecuciones;
- autenticación de la cuenta de Telegram desde la propia GUI;
- soporte para código de verificación y contraseña de dos pasos;
- listado automático de los grupos accesibles por la cuenta;
- selección de carpeta local mediante el explorador de Windows;
- opción para incluir archivos de subcarpetas;
- vista previa de la cola;
- progreso real del archivo actual;
- progreso total de la cola;
- velocidad media de transferencia;
- cancelación del envío;
- **historial persistente de envíos**;
- **prevención de archivos duplicados**;
- **recuperación de colas interrumpidas**;
- distribución portátil sin instalador;
- versión compilada que no requiere Python en el ordenador de destino;
- compilación local mediante `build_portable.bat`;
- compilación automática para Windows mediante GitHub Actions.

## Historial de envíos

TG Uploader guarda el historial local en:

```text
data\tg_uploader.db
```

La base SQLite registra, entre otros datos:

- fecha y hora;
- grupo de destino;
- archivo;
- tamaño;
- hash SHA-256;
- estado del envío;
- identificador del mensaje de Telegram cuando está disponible.

El historial puede abrirse desde la GUI mediante **Ver historial de envíos**.

## Prevención de duplicados

De forma predeterminada está activada la opción:

**Omitir archivos ya enviados al mismo grupo**

Antes de enviar un archivo, TG Uploader calcula su **SHA-256** y consulta el historial local.

Un archivo se considera duplicado cuando:

1. tiene el mismo contenido, es decir, el mismo SHA-256; y
2. ese contenido ya fue enviado anteriormente al mismo grupo.

Por lo tanto, cambiar únicamente el nombre del archivo no evita la detección.

El mismo archivo sí puede enviarse normalmente a un grupo diferente.

Para volver a enviar deliberadamente el mismo contenido al mismo grupo, desactive la prevención de duplicados antes de crear una nueva cola.

## Recuperación de colas interrumpidas

La cola se guarda en SQLite antes de iniciar el envío.

Después de procesar cada archivo se actualiza su estado. Si la aplicación se cierra, el ordenador se reinicia o falla la conexión:

- los archivos completados siguen completados;
- los duplicados ya omitidos siguen completados;
- los archivos pendientes continúan pendientes;
- el archivo que se estaba enviando vuelve al estado pendiente;
- los archivos con error pueden volver a intentarse.

Cuando existe una cola recuperable, **Reanudar cola interrumpida** queda disponible al iniciar de nuevo la aplicación.

### Limitación importante

La recuperación funciona **por archivo**, no desde un punto arbitrario de los bytes del archivo.

Si un archivo de 2 GB se interrumpe después de 1 GB, ese archivo concreto vuelve a empezar desde el principio. Los archivos completados anteriormente no se envían otra vez.

## Idiomas

El selector de idioma se encuentra en la cabecera:

- Português (Brasil);
- English;
- Español.

La preferencia se guarda en `data/config.json`.

## Versión portátil

La distribución compilada tiene aproximadamente esta estructura:

```text
TG-Uploader/
├── TG-Uploader.exe
├── _internal/
├── data/
├── README.md
├── README.en.md
├── README.es.md
└── PORTABLE.md
```

La carpeta completa puede moverse a otro directorio, disco externo o memoria USB.

El ordenador de destino **no necesita tener Python instalado**.

Consulte también [PORTABLE.md](PORTABLE.md).

## Datos portátiles y seguridad

La carpeta `data/` viaja con la aplicación y puede contener:

- configuración;
- historial y colas;
- API ID;
- API Hash;
- sesión autenticada de Telegram.

**No comparta ni publique la carpeta `data/`.**

Ya está incluida en `.gitignore`.

Si pierde una copia que contiene su sesión, revoque esa sesión en:

**Telegram → Ajustes → Dispositivos**

Para entregar una copia limpia a otra persona, distribuya la aplicación con la carpeta `data/` vacía.

## Requisitos de una versión portátil ya compilada

- Windows 10 o Windows 11;
- acceso a Internet;
- una cuenta de Telegram con acceso al grupo de destino;
- `api_id` y `api_hash` propios obtenidos en <https://my.telegram.org>.

Python no es necesario en el ordenador que ejecute una versión ya compilada.

## Crear las credenciales de la API de Telegram

1. Abra <https://my.telegram.org>.
2. Inicie sesión con la cuenta que utilizará con TG Uploader.
3. Abra **API development tools**.
4. Cree una aplicación.
5. Guarde **App api_id** y **App api_hash**.

Nunca publique su API Hash, código de verificación, contraseña o archivo de sesión.

## Generar la versión portátil con dos clics

El ordenador usado para compilar necesita Python 3.11 o posterior.

Después de descargar o clonar el repositorio, ejecute:

```text
build_portable.bat
```

La aplicación terminada quedará en:

```text
dist\TG-Uploader
```

Copie toda la carpeta `TG-Uploader`.

## Compilar mediante GitHub Actions

El workflow:

```text
.github/workflows/build-windows.yml
```

genera el artefacto:

```text
TG-Uploader-Windows-Portable
```

También puede iniciarse manualmente desde la pestaña **Actions** del repositorio.

## Ejecutar desde el código fuente

Clone el proyecto:

```powershell
git clone https://github.com/pablopcdossantos2-sys/tg-uploader.git
cd tg-uploader
```

Cree y active un entorno virtual:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Instale las dependencias:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Ejecute:

```powershell
python main.py
```

## Primer uso

1. Abra TG Uploader.
2. Seleccione el idioma.
3. Introduzca **API ID**.
4. Introduzca **API Hash**.
5. Introduzca el teléfono en formato internacional.
6. Haga clic en **Conectar y cargar grupos**.
7. Introduzca el código enviado por Telegram.
8. Introduzca la contraseña de dos pasos si se solicita.
9. Seleccione el grupo.
10. Seleccione la carpeta local.
11. Revise la cola.
12. Mantenga activada la protección contra duplicados o desactívela si es necesario.
13. Haga clic en **Iniciar envío**.

## Estructura del proyecto

```text
tg-uploader/
├── .github/
│   └── workflows/
│       └── build-windows.yml
├── build_portable.bat
├── main.py
├── PORTABLE.md
├── README.md
├── README.en.md
├── README.es.md
├── requirements.txt
└── src/
    ├── __init__.py
    ├── config.py
    ├── i18n.py
    ├── storage.py
    ├── telegram_service.py
    └── ui.py
```

## Referencias

- Telegram — API ID y API Hash: <https://core.telegram.org/api/obtaining_api_id>
- Telegram — Términos de servicio de la API: <https://core.telegram.org/api/terms>
- Telethon: <https://docs.telethon.dev/>
- PyInstaller: <https://pyinstaller.org/>

## Licencia

Todavía no definida. Añada una licencia apropiada antes de distribuir versiones públicas.
