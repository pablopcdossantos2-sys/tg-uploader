# TG Uploader

**Lea este README en otros idiomas:** [Português](README.md) · [English](README-en.md)

Aplicación de escritorio portátil para Windows destinada al envío de archivos desde carpetas locales a grupos y temas de Telegram, con interfaz gráfica, seguimiento de progreso, historial de envíos, prevención de duplicados y recuperación de colas interrumpidas.

> Proyecto independiente y no oficial. TG Uploader utiliza la API de Telegram mediante Telethon y no está afiliado a Telegram.

## 👤 Autoría y desarrollo

Aplicación de escritorio portátil para Windows desarrollada de forma independiente por Pablo Phillipe Cândido dos Santos, destinada al envío organizado de archivos desde carpetas locales a grupos y temas de Telegram, con seguimiento de progreso, historial, prevención de duplicados y recuperación de colas interrumpidas.

El desarrollo contó con el uso de herramientas de inteligencia artificial generativa como recurso auxiliar, manteniéndose bajo responsabilidad del autor la concepción, implementación, integración y verificación del proyecto.

Currículo Lattes: [http://lattes.cnpq.br/9500873674712528](http://lattes.cnpq.br/9500873674712528)

---

# Para quien solo quiere usar el programa

Si **no está familiarizado con Terminal, PowerShell, Python o GitHub**, esta es la parte más importante del README.

**No necesita instalar Python** ni escribir comandos para utilizar una versión portátil ya compilada.

## Paso 1 — Descargar la versión portátil

1. Abra la página del proyecto en GitHub.
2. Haga clic en la pestaña **Actions**.
3. Abra la ejecución más reciente de **Build portable Windows app** que tenga un indicador verde de éxito.
4. Baje hasta la sección **Artifacts**.
5. Haga clic en **TG-Uploader-Windows-Portable**.
6. El navegador descargará un archivo `.zip`.

> Si otra persona ya le entregó la carpeta portátil, puede omitir este paso.

## Paso 2 — Extraer el ZIP

1. Abra la carpeta **Descargas** de Windows.
2. Localice el ZIP descargado.
3. Haga clic con el botón derecho.
4. Elija **Extraer todo...**.
5. Seleccione una carpeta fácil de encontrar, por ejemplo:

```text
C:\Programas\TG-Uploader
```

6. Haga clic en **Extraer**.

No ejecute el programa directamente desde dentro del ZIP.

## Paso 3 — Abrir TG Uploader

Abra la carpeta extraída.

Localice:

```text
TG-Uploader.exe
```

Haga doble clic.

Windows puede mostrar una advertencia porque el ejecutable todavía no dispone de una firma digital comercial. Si confía en el archivo obtenido de este repositorio, utilice las opciones de Windows para continuar.

---

# Antes del primer uso: crear las credenciales de Telegram

Telegram exige que las aplicaciones que utilizan su API tengan:

- **API ID**
- **API Hash**

Normalmente solo necesita hacer esto una vez por cuenta.

## Si ya posee un App api_id y un App api_hash

Si anteriormente creó una aplicación de Telegram y ya posee:

- **App api_id**
- **App api_hash**

**no necesita crear otra aplicación solamente para utilizar TG Uploader**.

En ese caso:

1. abra <https://my.telegram.org>;
2. inicie sesión con la misma cuenta de Telegram;
3. abra **API development tools**;
4. localice el **App api_id** y el **App api_hash** de la aplicación que ya controla;
5. copie ambos valores;
6. introduzca el `App api_id` en el campo **API ID** de TG Uploader y el `App api_hash` en **API Hash**;
7. continúe normalmente con la autenticación de la cuenta.

Puede entonces **omitir el paso de creación de una nueva aplicación** explicado más abajo.

> Reutilice únicamente credenciales de una aplicación que le pertenezca o que esté autorizado a administrar. No utilice credenciales encontradas en Internet o entregadas por terceros desconocidos.

> No existe ninguna ventaja en crear varias aplicaciones de Telegram sin necesidad. Si sus credenciales actuales son válidas y tiene acceso a ellas, normalmente basta con reutilizarlas.

## Paso 1 — Entrar en el sitio de Telegram

1. Abra el navegador.
2. Acceda a:

<https://my.telegram.org>

3. Introduzca el teléfono de su cuenta en formato internacional.
4. Telegram enviará un código a su cuenta.
5. Introduzca ese código en el sitio.

## Paso 2 — Abrir API development tools

Después de iniciar sesión:

1. haga clic en **API development tools**;
2. compruebe primero si ya aparecen un **App api_id** y un **App api_hash**;
3. si esos datos ya existen para una aplicación que usted controla, reutilícelos y **no cree una aplicación nueva**;
4. cree una nueva aplicación solamente si todavía no dispone de credenciales adecuadas.

Ejemplo:

```text
App title: TG Uploader
Short name: tguploader
Platform: Desktop
```

## Paso 3 — Guardar API ID y API Hash

Aparecerán valores parecidos a:

```text
App api_id: 12345678
App api_hash: abcdef1234567890abcdef1234567890
```

Guarde ambos.

No publique su API Hash en capturas, foros, vídeos o commits de GitHub.

---

# Primer uso de TG Uploader

## Paso 1 — Elegir el idioma

En la parte superior seleccione:

- Português (Brasil)
- English
- Español

La aplicación recordará su elección.

De forma predeterminada, la ventana principal se abre **maximizada** para facilitar la visualización de la cola y del progreso.

Los campos que requieren introducir información muestran una pista dentro del propio campo, con un ejemplo o una indicación del valor esperado.

## Paso 2 — Introducir los datos de la cuenta

En **1. Cuenta de Telegram**:

1. introduzca el **API ID**;
2. pegue el **API Hash**;
3. escriba el teléfono en formato internacional.

Después de introducir **API ID** y **API Hash** por primera vez, TG Uploader los guarda localmente. La próxima vez que abra la aplicación, esos campos se rellenarán automáticamente y no tendrá que escribirlos de nuevo.

El **API ID** se guarda en `data/config.json` y el **API Hash** en `data/secrets.json`. Estos archivos pertenecen a su copia portátil de la aplicación.

> Si elimina el contenido de la carpeta `data/` o utiliza una copia limpia de TG Uploader, tendrá que introducir las credenciales nuevamente.

Ejemplo:

```text
+34612345678
```

## Paso 3 — Conectar con Telegram

Haga clic en:

**Conectar y cargar grupos**

La primera vez, Telegram enviará un código de verificación.

TG Uploader abrirá una pequeña ventana.

Introduzca el código y haga clic en **Confirmar**.

Si su cuenta utiliza verificación en dos pasos, aparecerá otra ventana solicitando esa contraseña.

## Paso 4 — Elegir el grupo y, si lo desea, un tema

Después de conectarse, TG Uploader cargará los grupos disponibles.

La lista está diseñada para evitar confusiones con los identificadores internos de Telegram. Siempre que sea posible, cada destino se muestra como:

```text
Nombre del grupo · Tipo · @username
```

Ejemplo:

```text
Equipo de Proyectos · Foro · @equipoproyectos
```

Si el grupo no tiene `@username`, la aplicación puede mostrar un **ID técnico**. Ese número solo sirve para distinguir entidades de Telegram con el mismo nombre; no necesita interpretarlo para elegir el destino.

Los grupos antiguos que Telegram migró a supergrupos se ignoran en la lista, evitando que aparezcan el grupo antiguo y el nuevo con el mismo nombre.

En **2. Destino — grupo y tema**:

1. abra la primera lista;
2. seleccione el grupo;
3. espere unos instantes mientras TG Uploader comprueba si ese grupo utiliza temas.

Si el grupo **no utiliza temas**, el selector de tema permanecerá deshabilitado.

Si el grupo **utiliza temas**, la segunda lista quedará disponible. Podrá elegir:

- **General / sin tema específico**; o
- un tema concreto identificado por su nombre e ID.

Ejemplo:

```text
Anuncios · 1234
```

Todos los archivos de esa cola se enviarán al tema seleccionado.

El tema queda guardado junto con la cola. Si el envío se interrumpe y se reanuda más tarde, los archivos restantes continuarán hacia el **mismo tema original**.

La cuenta debe tener permiso para enviar archivos a ese grupo.

> La prevención de duplicados también tiene en cuenta el tema. Un archivo enviado al tema A todavía puede enviarse al tema B del mismo grupo.

## Paso 5 — Elegir la carpeta local

En **3. Carpeta local**:

1. haga clic en **Buscar**;
2. navegue con el Explorador de Windows;
3. seleccione la carpeta que contiene los archivos;
4. confirme la selección.

Los archivos aparecerán en el lado derecho.

Mantenga activada **Incluir archivos de subcarpetas** si desea analizar también las subcarpetas.

## Paso 6 — Revisar la protección contra duplicados

De forma predeterminada está activada:

**Omitir archivos ya enviados al mismo destino (grupo/tema)**

Recomendamos mantenerla activada.

TG Uploader calcula el SHA-256 y comprueba si ese contenido ya fue enviado al mismo destino (grupo/tema).

Cambiar solamente el nombre del archivo no evita esta verificación.

## Paso 7 — Iniciar el envío

Haga clic en:

**Iniciar envío**

Durante el proceso verá:

- archivo actual;
- porcentaje;
- progreso total;
- número de archivos;
- bytes enviados;
- velocidad media.

Puede hacer clic en **Cancelar envío** en cualquier momento.

---

# Si el programa se cierra o falla Internet

No necesita empezar desde cero.

La cola se guarda en:

```text
data\tg_uploader.db
```

Cuando vuelva a abrir la aplicación, **Reanudar cola interrumpida** estará disponible si existe trabajo recuperable.

Los archivos ya terminados no se vuelven a enviar.

## Limitación importante

La recuperación funciona por archivo.

Ejemplo:

- archivo 1 terminado: no se repite;
- archivo 2 detenido al 50%: empieza nuevamente desde el principio;
- los archivos siguientes siguen pendientes.

Esta versión no reanuda un archivo desde el byte exacto donde fue interrumpido.

---

# Ver el historial de envíos

Haga clic en:

**Ver historial de envíos**

La ventana mostrará:

- fecha y hora;
- estado;
- grupo;
- archivo;
- tamaño.

El historial se almacena localmente en:

```text
data\tg_uploader.db
```

---

# Sobre la carpeta data

La carpeta:

```text
data\
```

puede contener:

- configuración;
- idioma;
- historial;
- colas pendientes;
- API ID;
- API Hash;
- sesión autenticada de Telegram.

**No comparta esta carpeta.**

Para entregar una copia limpia:

1. cierre TG Uploader;
2. copie toda la carpeta del programa;
3. vacíe `data\` en la copia;
4. entregue esa copia.

La otra persona podrá autenticar su propia cuenta.

---

# Utilizar TG Uploader desde una memoria USB

TG Uploader es portátil.

Copie toda la carpeta:

```text
TG-Uploader
```

a una memoria USB, disco externo o SSD externo.

No copie únicamente `TG-Uploader.exe`.

La carpeta `_internal` también es necesaria.

---

# Generar la versión portátil en su propio ordenador

Esta sección es para desarrolladores o usuarios que quieran producir su propio ejecutable.

Si solamente quiere utilizar TG Uploader, puede ignorar esta sección.

## Método más sencillo: build_portable.bat

### Paso 1 — Instalar Python

1. Abra <https://www.python.org/downloads/>.
2. Descargue una versión reciente de Python 3.
3. Abra el instalador.
4. En la primera pantalla active:

```text
Add Python to PATH
```

5. Haga clic en **Install Now**.
6. Espere a que termine.

### Paso 2 — Descargar el código

En GitHub:

1. haga clic en el botón verde **Code**;
2. elija **Download ZIP**;
3. abra Descargas;
4. haga clic con el botón derecho en el ZIP;
5. seleccione **Extraer todo...**.

### Paso 3 — Ejecutar la compilación

Dentro de la carpeta extraída localice:

```text
build_portable.bat
```

Haga doble clic.

Aparecerá una ventana negra. Es normal.

**No necesita escribir nada.**

El script realiza automáticamente:

- preparación del entorno;
- instalación de bibliotecas;
- validación del código;
- pruebas;
- compilación;
- creación de la carpeta portátil.

Cuando aparezca:

```text
Build concluido com sucesso.
```

la aplicación estará en:

```text
dist\TG-Uploader
```

---

# Ejecutar desde el código fuente — tutorial para principiantes

Esta parte utiliza PowerShell.

Solo es necesaria para desarrollar o probar directamente el código Python.

## Paso 1 — Abrir PowerShell en la carpeta correcta

1. Abra la carpeta del proyecto en el **Explorador de archivos**.
2. Haga clic en la barra de direcciones.
3. Borre la ruta.
4. Escriba:

```text
powershell
```

5. Pulse **Enter**.

Se abrirá una ventana azul o negra ya situada en la carpeta correcta.

Puede mostrar algo parecido a:

```text
PS C:\Users\SuNombre\Downloads\tg-uploader-main>
```

Su ruta será diferente. Es normal.

## Paso 2 — Crear un entorno virtual

Ejecute:

```powershell
python -m venv .venv
```

Pulse **Enter**.

Se creará una carpeta llamada `.venv`.

## Paso 3 — Activarlo

Ejecute:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si funciona, verá algo parecido a:

```text
(.venv) PS C:\...
```

### Si PowerShell bloquea los scripts

Puede omitir la activación y utilizar directamente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Paso 4 — Instalar las dependencias

Ejecute:

```powershell
python -m pip install --upgrade pip
```

Espere a que termine.

Después ejecute:

```powershell
python -m pip install -r requirements.txt
```

Aparecerán muchas líneas. Es normal.

Espere hasta que PowerShell vuelva a mostrar una línea de comandos.

## Paso 5 — Abrir TG Uploader

Ejecute:

```powershell
python main.py
```

La ventana de TG Uploader debería abrirse.

---

# Problemas comunes

## “python no se reconoce”

Pruebe:

```powershell
py --version
```

Si funciona, sustituya `python` por `py`.

Si ninguno funciona, reinstale Python y marque **Add Python to PATH**.

## PowerShell se abrió en otra carpeta

Cierre la ventana y repita:

1. abra la carpeta correcta;
2. haga clic en la barra de direcciones;
3. escriba `powershell`;
4. pulse Enter.

## El grupo no aparece

Compruebe que:

- la cuenta autenticada pertenece al grupo;
- tiene acceso al grupo;
- ha autenticado la cuenta correcta.

## No aparece “Reanudar cola interrumpida”

Solo se habilita cuando existe una cola incompleta en la base local.

## Un archivo duplicado fue omitido

Es normal si la protección está activada.

Desactive **Omitir archivos ya enviados al mismo destino (grupo/tema)** antes de crear una nueva cola si desea reenviar deliberadamente el mismo contenido.

---

# Estructura de la versión portátil

```text
TG-Uploader/
├── TG-Uploader.exe
├── _internal/
├── data/
├── README.md
├── README-en.md
├── README.es.md
└── PORTABLE.md
```

# Referencias

- Telegram — API ID y API Hash: <https://core.telegram.org/api/obtaining_api_id>
- Telegram — Términos de servicio de la API: <https://core.telegram.org/api/terms>
- Telethon: <https://docs.telethon.dev/>
- PyInstaller: <https://pyinstaller.org/>

# Licencia

Todavía no definida. Añada una licencia apropiada antes de distribuir versiones públicas.
