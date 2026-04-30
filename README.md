# Práctica 4: Uso de las Expresiones Regulares y Extensión de Software 🚀

**Instituto Politécnico Nacional (IPN) - Escuela Superior de Cómputo (ESCOM)**
**Unidad de Aprendizaje:** Teoría de la Computación
**Alumno:** Iker Saúl González Ortiz

---

## 📖 Descripción del Proyecto
Este repositorio contiene el software interactivo `app_omnibus.py`, desarrollado con la librería **Flet**. El programa es un entorno integral de Teoría de la Computación que permite explorar las expresiones regulares, simular Autómatas Finitos Deterministas (AFD) y No Deterministas (AFND), y convertir un AFD a su Expresión Regular equivalente utilizando el algoritmo de eliminación de estados.

## ⚙️ Requisitos e Instalación

Para ejecutar este proyecto, necesitas tener instalado **Python 3.8** o superior.

1. **Clona el repositorio:**
   ```bash
   git clone <URL_DE_TU_REPOSITORIO>
   cd <NOMBRE_DE_LA_CARPETA>
Instala las dependencias:Se recomienda usar un entorno virtual. Instala los requerimientos ejecutando:Bashpip install -r requirements.txt
Ejecuta el programa:Bash   python app_omnibus.py
🛠️ Funcionalidades del Software (Módulos)El software está dividido en 4 pestañas principales:Cadenas y Cerraduras: Cálculo de prefijos, sufijos y subcadenas.Simulador AFD & ER: Permite definir un AFD manualmente o importar archivos .jff de JFLAP. Incluye un simulador de cadenas y el motor de conversión a Expresión Regular (GNFA) paso a paso.Motor AFND: Permite definir transiciones de un AFND y simular el procesamiento de cadenas visualizando los estados activos en tiempo real.Validadores ER: Implementación práctica de Expresiones Regulares para validar Correos Electrónicos, Teléfonos a 10 dígitos y Fechas (DD/MM/YYYY), incluyendo retroalimentación de errores.📚 Ejercicio 1: Investigación Teórica sobre Expresiones RegularesConceptos FundamentalesLenguaje Regular: Es un lenguaje formal que puede ser expresado mediante una expresión regular, aceptado por un autómata finito (determinista o no determinista) o generado por una gramática regular.Expresiones Regulares (ER): Son secuencias de caracteres que forman un patrón de búsqueda. Sus componentes y operaciones fundamentales son:Unión ($a|b$): Ocurre $a$ o $b$.Concatenación ($ab$): Ocurre $a$ seguido inmediatamente por $b$.Cierre de Kleene ($a^*$): Ocurre $a$ cero o más veces.Jerarquía de Chomsky: Los lenguajes regulares ocupan el Tipo 3 en la Jerarquía de Chomsky. Son el tipo de lenguaje más restrictivo y sencillo, generados por gramáticas regulares y reconocidos por autómatas finitos.Teorema de Kleene: Establece la equivalencia fundamental en la teoría de autómatas: todo lenguaje que puede ser definido por una expresión regular puede ser reconocido por un autómata finito, y viceversa.5 Aplicaciones Prácticas de las ER en la Computación ModernaProcesamiento de texto y búsqueda de patrones:Uso: Buscar y reemplazar palabras específicas en editores de código o procesadores de texto.Ejemplo ER: \b[Aa]ut[oó]mata\b (Encuentra "Automata", "autómata", etc., asegurando que sea una palabra completa).Análisis léxico en compiladores:Uso: Agrupar caracteres del código fuente en "tokens" (palabras reservadas, identificadores, símbolos).Ejemplo ER: ^[a-zA-Z_][a-zA-Z0-9_]*$ (Valida el nombre de una variable en lenguajes como C++ o Python).Validación de datos en formularios web:Uso: Asegurar que la entrada del usuario tenga el formato correcto antes de enviarla a una base de datos (Ej. correos).Ejemplo ER: ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ (Valida la estructura típica de un email).Filtrado y manipulación de datos (Logs):Uso: Extraer IPs, fechas o mensajes de error específicos de un archivo de registro de servidor.Ejemplo ER: ^ERROR:.* (Filtra todas las líneas de un log que comienzan con un fallo crítico).Automatización de tareas en sistemas operativos:Uso: Herramientas de terminal en Linux Mint (como grep, sed o awk) utilizan ER para buscar archivos o manipular salidas de comandos en tuberías de bash.Ejemplo ER: ls | grep "\.jff$" (Lista únicamente los archivos del directorio que terminan en la extensión de JFLAP).
