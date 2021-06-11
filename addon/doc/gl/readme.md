# NVDA Unmute

* Autor: Oleksandr Gryshchenko
* Versión: 1.5
* Compatibilidade con NVDA: 2019.3 en diante
* Descargar [versión estable][1]

Este complemento comproba o estado do sistema de audio de Windows cando NVDA se inicia. E, se resulta que o son está silenciado - o complemento forza a súa activación.

Ó mesmo tempo, compróbase o nivel de volume de forma separada para o proceso de NVDA.

O complemento tamén comproba o estado do sintetizador de voz. Se hai problemas coa súa inicialización, realízanse intentos para inicialo, que está especificado nas opcións de NVDA.

Hai unha oportunidade adicional para comprobar a qué dispositivo de son está saíndo NVDA. E, se este dispositivo difire do dispositivo predeterminado, a saída cambia automaticamente ao dispositivo de son instalado no sistema como o principal.

Nota: Se o son de inicio do complemento se reproduce aínda que o volume do NVDA estea activo. Isto significa, que o complemento cambia a saída ó disppositivo principal de son cada vez que inicias NVDA.

Isto ocorre cando o dispositivo de son de saída nas opcións de NVDA difire do dispositivo de son predeterminado ou "Microsoft Sound Mapper".

Isto pódese resolver facilmente dun dos seguintes xeitos:

1. Despois de reiniciar NVDA, soamente garda a configuración actual utilizando NVDA+Ctrl+C. O dispositivo de son predeterminado gardarase nas opcións de NVDA e o cambio non ocorrerá cada vez que NVDA se inicie.
2. Se non queres cambiar a configuración de NVDA - só deshabilita a función de cambiar o dispositivo de son no panel de opcións de Unmute.

## Diálogo de opcións do complemento
Para abrir o panel de opcións do complemento, segue estes pasos:

* Preme NVDA+N para abrir o menú NVDA.
* Logo vai a "Preferencias" -> "Opcións..." e na lista de categorías busca e abre "Unmute Windows audio".

Iso é todo, xa podes utilizar a tecla tab para moverte entre as opcións do complemento.

As seguintes opcións están dispoñibles no diálogo de opcións do complemento:

1. O primeiro deslizador no diálogo de opcións do complemento permíteche especificar o nivel de volume windows, que se establecerá cando inicies NVDA se o son se silenciase anteriormente ou fose demasiado baixo.

2. O volume de windows mínimo no cal se aplicará o procedemento de suba de volume. Este deslizador permíteche axustar o nivel de sensibilidade do complemento.

    Se o nivel de volume baixa a menos do nivel especificado aquí, o volume incrementarase a próxima vez que inicies NVDA.

    Noutro caso, se o nivel de volume permanece máis alto có nivel especificado aquí, cando reinicies NVDA, o seu nivel non mudará.

    E, por suposto, se o son estaba previamente desactivado, ao reiniciar o complemento activarao en calquera caso.

3. A seguinte caixa de verificación permite activar a reinicialización do controlador do sintetizador de voz.

    Este procedemento só iniciará se se detecta no inicio de NVDA que o controlador do sintetizador de voz non se inicializou.

4. Neste campo podes especificar o número de intentos de reinicializar o controlador do sintetizador de voz. Os intentos realízanse ciclicamente cun intervalo de 1 segundo. Un valor de 0 significa que os intentos se realizará indefinidamente ata que se complete o procedemento con éxito.

5. A opción "Cambiar ao dispositivo predeterminado de saída de audio" permite comprobar ó inicio o dispositivo de son ó que o NVDA está saíndo. E, se este dispositivo difire do dispositivo predeterminado, a saída cambia automaticamente ó dispositivo de son instalado no sistema como o principal.

6. A seguinte caixa de verificación activa ou desactiva a reprodución do son de inicio cando a operación é exitosa.

## compoñentes de terceiros
O complemento utiliza os seguintes compoñentes de terceiros:

* Para a interacción coa **Windows Core Audio API** - [módulo PyCaw](https://github.com/AndreMiras/pycaw/) distribuído baixo a licenza MIT.
* Para obter a información sobre procesos en execución e usar o compoñente PyCaw - [módulo psutil](https://github.com/giampaolo/psutil) distribuído baixo licenza BSD-3.

## Rexistro de trocos

### Versión 1.5.5
* o complemento probouse para compatibilidade con NVDA 2021.1;
* actualizado o módulo de terceiros **psutil**;
* o add-on adáptase para soportar as versións 3.7 e 3.8 de Python;
* engadidas anotacións de tipo MyPy ó código fonte do complemento;
* engadida a característica "Cambiar ao dispositivo predeterminado de saída de audio";
* os parámetros dos complementos almacénanse sempre no perfil de configuración base.

### Versión 1.4
* engadido un método para incrementar o volume de inicio de forma separada para o proceso NVDA;
* cambiado o son da notificación de operación exitosa (grazas a Manolo);
* tódalas funcións de control manual do volume se transferiron ó complemento de NVDA Volume Adjustment.

### Versión 1.3
* engadida a posibilidade de controlar o volume do dispositivo de son principal e de xeito separado para cada programa en execución;
* actualizada a tradución ao vietnamita (grazas a Dang Manh Cuong);
* engadida tradución turca (grazas a Cagri Dogan);
* Engadida tradución italiana (grazas a Christianlm);
* engadida tradución china simplificada (grazas a Cary Rowen);
* engadida tradución polaca (grazas a Stefan Banita);
* actualizada tradución ucrainiana;
* actualizado Leme.

### Versión 1.2
* cambio para usar **Core Audio Windows API** no canto de **Windows Sound Manager**;
* engadida reprodución de son de inicio cando o audio se activa con éxito dende o complemento.

### Versión 1.1
* engadido diálogo de opcións do complemento;
* actualizada tradución ucrainiana.

### Versión 1.0.1
* Realiza intentos repetidos de habilitar o controlador de síntese no caso da súa inicialización falida;
* engadida tradución vietnamita por Dang Manh Cuong;
* engadida tradución ucrainiana.

### Versión 1.0. Características de implementación
O complemento utiliza un módulo de terceiros Windows Sound Manager.

## Alteración do código fonte do complemento
Poderías clonar este repo para facer alteración a NVDA Unmute.

### Dependencias de terceiros
Pódense instalar con pip:

- markdown
- scons
- python-gettext

### Para empaquetar o complemento para distribución
1. Abre unha liña de ordes, cambia á raíz deste repo
2. Executa a orde **scons**. O complemento creado, se non houbo erros, estará situado no directorio actual.

[1]: https://addons.nvda-project.org/files/get.php?file=unmute
