# NVDA Unmute

* Autor: Oleksandr Gryshchenko
* Versión: 1.5
* Compatibilidad con NVDA: 2019.3 y posteriores
* Descargar [versión estable][1]

Este complemento comprueba el estado del sonido en Windows cuando NVDA se inicia y, si determina que el sonido está silenciado, el complemento fuerza su activación.

Al mismo tiempo, se comprueba por separado el volumen del proceso de NVDA.

El complemento también comprueba el estado del sintetizador de voz. Si hay problemas durante su inicialización, se hacen intentos para iniciarlo, tal y como se especifica en las opciones de NVDA.

Hay una posibilidad adicional que comprueba el dispositivo de sonido por el que sale NVDA. Si este dispositivo es distinto del predeterminado, se alterna automáticamente la salida al dispositivo predeterminado instalado en el sistema.

Nota: siempre se reproduce el sonido de inicio del complemento, incluso si el volumen está activado. Esto es porque el complemento conmuta la salida al dispositivo de sonido principal cada vez que NVDA se inicia.

Esto sucede cuando el dispositivo de sonido de salida configurado en las opciones de NVDA difiere del dispositivo de salida predeterminado o del "Asignador de sonido Microsoft".

Esto se puede resolver de una de las siguientes formas:

1. Después de reiniciar NVDA, guarda la configuración actual pulsando NVDA+ctrl+c. Se guardará el dispositivo de sonido predeterminado en los ajustes de NVDA y la conmutación no se producirá cada vez que NVDA se inicie.
2. Si no quieres cambiar la configuración de NVDA, simplemente desactiva la función de alternar dispositivos de sonido en el panel de opciones de Unmute.

## Diálogo de opciones del complemento
Para abrir el panel de opciones del complemento, sigue estos pasos:

* Pulsa NVDA+n para abrir el menú NVDA.
* Después ve a "Preferencias" -> "Opciones..." y busca en la lista de categorías "Unmute Windows Audio".

Eso es todo, ahora puedes usar el tabulador para desplazarte por las opciones del complemento.

Las siguientes opciones están disponibles en el diálogo de opciones del complemento:

1. El primer deslizador del diálogo de opciones del complemento te permite especificar el nivel de volumen de Windows que se configurará cuando inicies NVDA si el sonido estaba silenciado o el volumen estaba muy bajo.

2. El nivel de volumen mínimo de Windows para que se aplique el procedimiento de incremento de volumen. Este deslizador te permite ajustar el nivel de sensibilidad del complemento.

    Si el volumen cae por debajo del valor indicado aquí, este aumentará la próxima vez que inicies NVDA.

    De lo contrario, si el volumen es mayor que el valor que se indique aquí, el nivel no cambiará al reiniciar NVDA.

    Y, por supuesto, si el sonido estaba apagado, se encenderá al reiniciar el complemento.

3. La siguiente casilla de verificación permite habilitar la reinicialización del controlador de sintetizador de voz.

    Este procedimiento sólo se iniciará si se detecta que el controlador del sintetizador de voz no se ha iniciado tras arrancar NVDA.

4. En el siguiente campo puedes indicar el número de intentos de reinicialización del sintetizador. Los intentos se realizan cíclicamente en intervalos de un segundo. Un valor de 0 significa que se realizarán intentos indefinidamente hasta que el procedimiento se complete con éxito.

5. La opción "Switch to the default output audio device" permite comprobar al iniciar el dispositivo de salida de sonido de NVDA. Si este dispositivo difiere del predeterminado, se alterna automáticamente la salida al dispositivo de sonido instalado en el sistema como principal.

6. La siguiente casilla de verificación activa o desactiva la reproducción de un sonido de inicio cuando la operación tiene éxito.

## Componentes de terceros
El complemento utiliza los siguientes componentes de terceros:

* Para interactuar con la **API de Windows Core Audio** - [módulo PyCaw](https://github.com/AndreMiras/pycaw/), distribuido bajo la licencia MIT.
* Para obtener información sobre procesos en ejecución y usar en componente PyCaw - [módulo psutil](https://github.com/giampaolo/psutil), distribuido bajo la licencia BSD-3.

## Registro de cambios

### Versión 1.5.5
* se ha probado la compatibilidad del complemento con NVDA 2021.1;
* se ha actualizado el módulo de terceros psutil;
* se ha adaptado el complemento para soportar las versiones de Python 3.7 y 3.8;
* Añadidas anotaciones de MyPy al código fuente;
* añadida función "Cambiar al dispositivo de salida predeterminado";
* los parámetros del complemento siempre se alojan en el perfil de configuración base.

### Versión 1.4
* añadido un método para aumentar el volumen del proceso NVDA por separado al iniciar;
* cambiado el sonido de operación exitosa (gracias a Manolo);
* todas las funciones manuales para controlar el volumen se han transferido al complemento de ajuste de volumen para NVDA.

### Versión 1.3
* añadida la capacidad de controlar de forma separada el volumen principal y de cada programa;
* actualizada traducción al vietnamita (gracias a Dang Manh Cuong);
* añadida la traducción al turco (gracias a Cagri Dogan);
* Añadida la traducción al italiano (gracias a Christianlm);
* añadida la traducción al chino simplificado (gracias a Cary Rowen);
* Polish translation added (thanks to Stefan Banita);
* actualizada traducción al ucraniano;
* actualizada la documentación.

### Versión 1.2
* ahora se usa la API Windows Audio Core en vez del administrador de sonido de Windows;
* se añade la reproducción de un sonido de inicio cuando el complemento activa con éxito el audio.

### Versión 1.1
* añadido diálogo de opciones del complemento;
* actualizada traducción al ucraniano.

### Versión 1.0.1
* Realiza intentos repetidos para activar el controlador del sintetizador en caso de inicialización fallida;
* Añadida traducción al vietnamita por Dang Manh Cuong;
* Añadida traducción al ucraniano.

### Versión 1.0. Características de la implementcaión
El complemento usa un módulo de terceros, Windows Sound Manager.

## Alteración del código fuente del complemento
Puedes clonar este repositorio para alterar NVDA Unmute.

### Dependencias de terceros
Se pueden instalar con Pip:

- markdown
- scons
- python-gettext

### Para empaquetar el complemento
1. Abre una línea de órdenes, navega a la raíz de este repositorio
2. Ejecuta la orden **scons**. El complemento creado, si no hay errores, se sitúa en el directorio actual.

[1]: https://addons.nvda-project.org/files/get.php?file=unmute
