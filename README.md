# Laboratorio 4
* Yefri Stiven Barrero Solano - 2320392
* Jose Alejandro Mesa Chaves - 2291048
* Juan Dvid Becerra Pulido - 2283133

# Simulación Avanzada de Formación de Drones usando Optimización por Enjambre de Partículas (PSO)

El código  `PSO_Drones.py` implementa una simulación de drones que utilizan el algoritmo de Optimización por Enjambre de Partículas (PSO, por sus siglas en inglés) para formar figuras complejas en un espacio aéreo bidimensional. El código, escrito en Python, incorpora características avanzadas como tolerancia a fallos (donde un dron puede "fallar" durante la simulación y el sistema se adapta), evación de obstáculos, penalizaciones por colisiones y optimización de energía. Se generan animaciones visuales para tres formaciones personalizadas: "dragon" (dragón), "robot" y "star" (estrella), además de una formación circular básica.

PSO es un algoritmo bioinspirado basado en el comportamiento de enjambres (como aves o peces), donde cada "partícula" (en este caso, un dron) ajusta su posición y velocidad influenciada por su mejor posición personal, la mejor posición global del enjambre y factores inerciales. Esta técnica es comúnmente usada en robótica de enjambres para tareas como búsqueda, rescate o espectáculos aéreos, ya que permite una coordinación descentralizada y robusta ante perturbaciones.

Al ejecutar el código, se obtienen los siguientes resultados para cada formación ("dragon", "robot" y "star"):

- **Convergencia exitosa**: En la mayoría de las ejecuciones, los drones activos forman la figura objetivo en 40 iteraciones, con una aptitud final baja (por ejemplo, alrededor de 0.1-0.5, dependiendo de la complejidad de la formación y la posición inicial aleatoria). La aptitud mide la distancia al objetivo, penalizaciones por obstáculos/colisiones y energía.
- **Manejo de fallos**: En la iteración 20 (mitad de 40), un dron aleatorio falla (excepto el mejor), y el sistema recalcula la formación con 14 drones. Esto resulta en una redistribución suave, aunque con una ligera degradación en la precisión de la forma (por ejemplo, en "star", las puntas pueden ser menos definidas).
- **Evitación de obstáculos**: Los drones evitan los tres obstáculos circulares definidos (centros en [-2,1], [3,-2] y [0,-3]), con penalizaciones que guían el movimiento. En animaciones, se observa cómo los drones rodean estos áreas rojas.
- **Animaciones generadas**: Para cada formación, se crea un archivo GIF (e.g., `drones_dragon_animation.gif`) que muestra la evolución frame por frame. Los drones activos son azules, inactivos grises, el mejor dron rojo, y la formación objetivo en verde. Las animaciones confirman una convergencia gradual, con exploración inicial y explotación final.
- **Métricas de rendimiento**: Durante la ejecución, se imprimen actualizaciones cada 10 iteraciones, como "Iteración 40: Mejor aptitud = 0.123, Drones activos: 14/15". La aptitud global disminuye consistentemente, validando la optimización.
- **Limitaciones observadas**: En formaciones complejas como "robot", la silueta puede no ser perfecta debido a la aproximación matemática; además, posiciones iniciales muy alejadas pueden requerir más iteraciones. No se simulan dinámicas físicas reales (e.g., viento), lo que podría mejorarse en extensiones.

## Paso a Paso Realizado

El código se estructura en una clase `AdvancedDroneFormationPSO` que encapsula la inicialización, navegación, fitness y visualización. A continuación, un desglose paso a paso:

### 1. Inicialización (`__init__`)
- **Parámetros**: Número de drones (15), iteraciones máximas (60), tipo de formación ('dragon' por defecto).
- **Espacio aéreo**: Límites de [-8, 8] en X e Y.
- **Formación objetivo**: Generada por `create_formation`, que usa ecuaciones paramétricas para crear puntos en la forma deseada (e.g., para 'dragon', combina cosenos y senos para una silueta ondulada).
- **Obstáculos**: Lista de diccionarios con centros y radios.
- **Posiciones iniciales**: Drones colocados aleatoriamente; velocidades en cero.
- **Tolerancia a fallos**: Lista de drones activos (todos True inicialmente); mejor posición personal y global calculadas con `fitness`.
- **Historial**: Lista para almacenar posiciones por iteración, usada en animaciones.

### 2. Generación de Formaciones (`create_formation`)
- Usa `np.linspace` para ángulos uniformes.
- Para 'circle': Posiciones circulares simples.
- Para 'dragon': Ecuación armónica compleja para una forma serpenteante.
- Para 'robot': Segmentos condicionales para cabeza (semicírculo), cuerpo (rectángulo aproximado) y piernas.
- Para 'star': Radios alternados para puntas de estrella.
- Esto permite personalización; se podría extender a más formas (e.g., 'heart').

### 3. Simulación de Fallos (`simulate_failure`)
- En la iteración media (e.g., 20 de 40), selecciona un dron activo aleatorio (no el mejor) y lo desactiva.
- Recalcula la formación objetivo con el número reducido de drones activos.
- Imprime un mensaje de fallo para trazabilidad.

### 4. Función de Aptitud (`fitness`)
- Para drones inactivos: Retorna infinito (penalización).
- **Componentes**:
  - Distancia euclidiana al objetivo (reasignado si hay fallos).
  - Penalización por obstáculos: Alta si dentro, decreciente si cerca.
  - Penalización por colisiones: Si <0.5 unidades de otro dron activo.
  - Penalización por energía: Proporcional a la magnitud de la velocidad.
- Esto multi-objetivo asegura seguridad y eficiencia.

### 5. Navegación Principal (`navigate`)
- Bucle por iteraciones:
  - Llama a `simulate_failure`.
  - Para cada dron activo: Calcula velocidad con inercia (0.8), memoria (1.5*r1) y social (1.5*r2).
  - Actualiza posición, clip a límites.
  - Evalúa fitness; actualiza mejores personales/globales si mejora.
- Almacena historial; imprime métricas cada 10 iteraciones.
- Retorna mejor posición y fitness final.

### 6. Visualización (`visualize_navigation`)
- Usa Matplotlib para figura con obstáculos (círculos rojos), objetivos (puntos verdes).
- Scatter plots para drones activos (azul), inactivos (gris) y mejor (rojo).
- Animación con `FuncAnimation`: Actualiza posiciones por frame; aproxima mejor dron en runtime.
- Guarda GIF con Pillow; muestra plot interactivo.

### 7. Ejecución Principal
- Itera sobre formaciones ['dragon', 'robot', 'star'].
- Instancia clase, navega, imprime resultados, visualiza.

# Simulación de Búsqueda de Supervivientes con Drones usando Optimización por Colonia de Hormigas (ACO)

El código  `ACO.py` implementa una simulación de drones autónomos que utilizan el algoritmo de Optimización por Colonia de Hormigas (ACO, por sus siglas en inglés) para buscar supervivientes y recursos en una zona de desastre bidimensional. El código, escrito en Python, modela un entorno dinámico con obstáculos (escombros), supervivientes y recursos, donde los drones exploran guiados por feromonas, heurísticas y exploración aleatoria. La simulación incluye características avanzadas como obstáculos dinámicos, evaporación de feromonas y asignación adaptativa de objetivos, con visualización a través de animaciones GIF y gráficos de métricas.

ACO es un algoritmo bioinspirado basado en el comportamiento de las hormigas, que depositan feromonas para marcar caminos hacia recursos. En este contexto, los drones actúan como hormigas, navegando un grid para maximizar la cobertura del área, encontrar supervivientes y recolectar recursos, mientras evitan obstáculos. Esta técnica es aplicable en escenarios reales como misiones de búsqueda y rescate tras desastres naturales.

Al ejecutar el código con 12 drones en un grid de 30x30 durante 150 iteraciones, se obtienen los siguientes resultados:

- **Búsqueda de supervivientes**: En la mayoría de las ejecuciones, los drones encuentran todos los 15 supervivientes en menos de 150 iteraciones (a menudo entre 80-120 iteraciones), dependiendo de la distribución inicial aleatoria de supervivientes y obstáculos. Por ejemplo, una ejecución típica reporta "¡Todos los supervivientes encontrados en la iteración 97!".
- **Cobertura del área**: La cobertura final suele superar el 85-90% del área accesible (excluyendo celdas con obstáculos), indicando una exploración efectiva. Por ejemplo, una salida muestra "Cobertura final: 89.47%".
- **Consumo de energía**: La energía total consumida (suma de movimientos de todos los drones) varía entre 1500-2000 unidades, reflejando la exploración activa. Cada movimiento consume 1 unidad de energía.
- **Obstáculos dinámicos**: Los nuevos escombros añadidos cada 20 iteraciones (en iteración 10, 30, etc.) obligan a los drones a recalcular rutas, lo que se observa en la animación como desviaciones en los caminos.
- **Visualización**: Se genera un archivo GIF (`drones_ant_simulation.gif`) que muestra el grid (blanco: libre, negro: obstáculos, verde: supervivientes, azul: recursos), drones (rojo), áreas visitadas (amarillo translúcido) y métricas en pantalla (cobertura, supervivientes, energía). Además, se produce una imagen PNG (`drones_ant_metrics.png`) con tres gráficos: cobertura, energía y supervivientes vs. iteraciones.
- **Rendimiento**: El tiempo de simulación es razonable, típicamente 5-10 segundos en hardware estándar, aunque depende del equipo. Por ejemplo: "Tiempo de simulación: 7.23 segundos".
- **Limitaciones observadas**: En algunas ejecuciones, los drones pueden concentrarse en áreas con altas feromonas, retrasando la exploración de regiones lejanas. La aleatoriedad en la inicialización puede llevar a variaciones en el número de iteraciones necesarias. No se modelan dinámicas físicas complejas (e.g., consumo variable de batería por distancia).

En general, los resultados validan ACO como una estrategia robusta para búsqueda distribuida, con capacidad de adaptación a entornos dinámicos, alineándose con aplicaciones como las operaciones de rescate de la Cruz Roja o sistemas de drones autónomos.

## Paso a Paso Realizado

El código se organiza en tres clases principales: `DisasterZone` (entorno), `AntDrone` (drones individuales) y `ACODroneSwarm` (coordinación del enjambre). A continuación, un desglose paso a paso:

### 1. Clase `DisasterZone` (Inicialización del Entorno)
- **Parámetros**: Grid de 30x30 celdas.
- **Grid principal**: Matriz NumPy donde 0=terreno libre, 1=obstáculo, 2=superviviente, 3=recurso.
- **Inicialización** (`initialize_zone`):
  - Obstáculos: 40 clusters de escombros de tamaño 1-3 celdas, colocados aleatoriamente con probabilidad 0.7.
  - Supervivientes: 15 celdas libres aleatorias marcadas como 2.
  - Recursos: 10 celdas libres aleatorias marcadas como 3.
- **Feromonas y visitas**: Matrices separadas (`pheromone_grid`, `visited_grid`) para rastrear feromonas y celdas visitadas.
- **Obstáculos dinámicos** (`add_dynamic_obstacle`): Cada 20 iteraciones, añade un cluster de escombros (tamaño 2-4) con probabilidad 0.6.
- **Evaporación de feromonas** (`evaporate_pheromones`): Reduce feromonas en 10% por iteración.
- **Funciones auxiliares**: `deposit_pheromone` (añade feromonas), `mark_visited` (marca celdas visitadas), `get_coverage_percentage` (calcula cobertura de celdas accesibles).

### 2. Clase `AntDrone` (Comportamiento de Drones)
- **Inicialización**: Cada dron tiene posición (x, y), ID, referencia al `DisasterZone`, y métricas (supervivientes/recursos encontrados, energía).
- **Movimiento** (`move`):
  - Si tiene objetivo (`has_target`), usa `move_toward_target` para acercarse (priorizando pasos en X o Y, o el vecino más cercano al objetivo si hay obstáculos).
  - Sin objetivo: Selecciona un vecino válido (no obstáculo) basado en probabilidades ACO:
    - **Feromonas**: `pheromone ** alpha` (α=1 por defecto).
    - **Heurística**: Prioriza celdas no visitadas (x2), supervivientes (x5) o recursos (x3).
    - **Exploración**: Con probabilidad 0.1, aplica un factor aleatorio (1-3).
  - Normaliza probabilidades y elige un vecino; actualiza posición, energía (+1), marca celda visitada y deposita feromonas (10 unidades base).
- **Revisión de contenido** (`check_cell_content`): Si encuentra un superviviente (2), lo elimina, suma 1 a `survivors_found`, deposita feromonas extra (x5). Si encuentra un recurso (3), lo elimina, suma 1 a `resources_found`, deposita feromonas extra (x3).
- **Vecinos válidos** (`get_valid_neighbors`): Retorna celdas adyacentes (8 direcciones) dentro de límites y sin obstáculos.
- **Objetivos** (`set_target`): Asigna una posición objetivo (x, y).

### 3. Clase `ACODroneSwarm` (Coordinación del Enjambre)
- **Inicialización**: Crea un `DisasterZone` y 12 drones en posiciones libres aleatorias. Registra estado inicial (posiciones, grid, cobertura, energía, supervivientes).
- **Iteración** (`run_iteration`):
  - Evapora feromonas.
  - Mueve cada dron.
  - Cada 20 iteraciones, añade un obstáculo dinámico.
  - Cada 15 iteraciones, asigna objetivos a drones ociosos basado en celdas con feromonas altas (percentil 80).
- **Simulación** (`run_simulation`):
  - Ejecuta hasta 150 iteraciones o hasta encontrar todos los supervivientes.
  - Imprime métricas cada 20 iteraciones (cobertura, supervivientes, energía).
  - Reporta tiempo de simulación, cobertura final, supervivientes y energía.
- **Visualización** (`visualize_simulation`):
  - Usa Matplotlib con `FuncAnimation` para mostrar el grid (colores: blanco=libre, negro=obstáculos, verde=supervivientes, azul=recursos), drones (rojo), áreas visitadas (amarillo translúcido).
  - Muestra métricas en un cuadro de texto (cobertura, supervivientes, energía).
  - Guarda animación como `drones_ant_simulation.gif`.
- **Métricas** (`plot_metrics`):
  - Genera tres gráficos: cobertura (%), energía total, supervivientes encontrados vs. iteraciones.
  - Guarda como `drones_ant_metrics.png`.

### 4. Ejecución Principal
- Configura 12 drones, grid 30x30, 150 iteraciones, α=1, β=2, exploración=0.1.
- Crea y ejecuta `ACODroneSwarm`, genera animación y gráficos.

# Simulación de Polinización en Invernadero con Drones usando Algoritmo de Colonia de Abejas (ABC)

El código  `ABC.py` implementa una simulación de drones autónomos que realizan tareas de polinización en un invernadero bidimensional, utilizando el Algoritmo de Colonia de Abejas (ABC, por sus siglas en inglés). El código, escrito en Python, modela un entorno con flores de diferentes niveles de madurez, estaciones de carga y tres tipos de drones (obreros, observadores y exploradores), cada uno con roles específicos inspirados en el comportamiento de las abejas. La simulación incluye dinámicas como consumo de batería, recarga, maduración de flores y visualización mediante animaciones GIF y gráficos de métricas.

ABC es un algoritmo bioinspirado basado en el comportamiento de las abejas en la búsqueda de néctar. Los drones emulan abejas obreras (explotan recursos conocidos), observadoras (siguen patrones de alta calidad) y exploradoras (buscan nuevas áreas), optimizando la polinización de 50 flores en un grid de 20x20. Esta técnica es relevante para aplicaciones en agricultura de precisión, como la polinización en invernaderos automatizados.

## Resultados Obtenidos

Al ejecutar el código con 8 obreros, 4 observadores, 3 exploradores en un invernadero de 20x20 durante 200 iteraciones, se obtienen los siguientes resultados:

- **Polinización**: La polinización promedio alcanza entre 75-85% al final de la simulación, con 35-45 de las 50 flores superando el 80% de polinización. Por ejemplo, una salida típica reporta "Polinización promedio: 81.2%, Flores bien polinizadas (>80%): 42/50".
- **División de trabajo**: Los obreros polinizan la mayoría de las flores (e.g., 20-25 flores), los observadores contribuyen significativamente (e.g., 10-15 flores), y los exploradores polinizan menos (e.g., 5-10 flores), pero ayudan a descubrir nuevas flores.
- **Energía**: La energía total (suma de baterías de todos los drones) disminuye gradualmente debido al consumo, con picos de recuperación cuando los drones recargan. Al final, la energía total suele estar entre 1000-1200 unidades (de un máximo de 1500, con 15 drones a 100%).
- **Visitas a flores**: El número total de visitas varía entre 150-200, reflejando múltiples visitas a flores maduras. Las flores con alta madurez (4-5) reciben más visitas, como se esperaba.
- **Visualización**: Se genera un archivo GIF (`bee_drones_simulation.gif`) que muestra:
  - Flores (verde, intensificándose con polinización; tamaño por madurez).
  - Drones (amarillo: obreros, naranja: observadores, rojo: exploradores; tamaño por batería; etiqueta con inicial de estado).
  - Estaciones de carga (cuadrados negros).
  - Métricas en pantalla (polinización promedio, energía total, visitas).
  - También se produce una imagen PNG (`bee_drones_metrics.png`) con cuatro gráficos: polinización promedio, energía total, visitas totales y contribución por tipo de dron.
- **Rendimiento**: El tiempo de simulación es de 5-10 segundos en hardware estándar. Por ejemplo: "Tiempo: 6.87s".
- **Limitaciones observadas**: En algunas ejecuciones, los drones se concentran en flores cercanas, retrasando la polinización de flores lejanas. La aleatoriedad en la inicialización puede causar variaciones en la polinización final. No se modelan obstáculos ni interacciones físicas complejas (e.g., viento).

En general, los resultados confirman que ABC es efectivo para coordinar drones en tareas de polinización, con una clara diferenciación de roles que mejora la eficiencia, alineándose con aplicaciones en agricultura de precisión, como los sistemas de polinización de DroneSeed.

## Paso a Paso Realizado

El código se organiza en tres clases principales: `Greenhouse` (invernadero), `BeeDrone` (drones individuales) y `ABCDroneSwarm` (coordinación del enjambre). A continuación, un desglose paso a paso:

### 1. Clase `Greenhouse` (Inicialización del Entorno)
- **Parámetros**: Grid de 20x20.
- **Flores**: Lista de 50 flores con:
  - Posición (x, y) aleatoria.
  - Madurez (1-5, aleatoria).
  - Nivel de polinización (inicialmente 0%).
  - Número de visitas (inicialmente 0).
  - ID único.
- **Estaciones de carga**: 4 estaciones en posiciones fijas ([2,2], [17,17], [17,2], [2,17]) con capacidades de 2-3 drones.
- **Actualización** (`update_flowers`):
  - Maduración: Incrementa madurez (máximo 5) con probabilidad 0.02.
  - Decaimiento: Reduce polinización en 2% con probabilidad 0.05 si >0.

### 2. Clase `BeeDrone` (Comportamiento de Drones)
- **Inicialización**: Posición (x, y), ID, tipo (obrero/observador/explorador), referencia al `Greenhouse`, batería (100%), estado (‘exploring’), eficiencia de polinización (1.0/0.8/0.6), factor de exploración (0.1/0.05/0.3).
- **Actualización de batería** (`update_battery`):
  - En ‘charging’: Aumenta batería en 5% por iteración; cambia a ‘exploring’ si ≥95%.
  - Otros estados: Consume 0.5 unidades por distancia recorrida; cambia a ‘returning’ si batería <20%.
- **Estación de carga** (`find_nearest_charging_station`): Selecciona la estación más cercana (distancia euclidiana).
- **Movimiento** (`move_toward_target`): Mueve hacia objetivo con velocidad 0.3; registra distancia recorrida.
- **Conocimiento de flores** (`update_known_flowers`): Añade flores a menos de 3 unidades a `known_flowers`; actualiza `flower_memory` con puntaje de calidad (madurez * polinización/100).
- **Selección de flores** (`select_flower_abc`):
  - **Obreros**: Priorizan flores conocidas con alta calidad, penalizando visitas (1 - 0.1*visitas).
  - **Observadores**: Priorizan flores maduras con baja polinización (bono 2*madurez, penalización 1 - polinización/100).
  - **Exploradores**: Priorizan flores menos visitadas (1 - 0.2*visitas) con factor aleatorio (0.5-1.5).
  - Usa probabilidades normalizadas para seleccionar flor.
- **Polinización** (`pollinate_flower`): Aumenta polinización en (5 + madurez) * eficiencia; incrementa visitas; registra flores polinizadas si ≥100%.
- **Actualización** (`update`):
  - Actualiza batería y flores conocidas.
  - En ‘returning’: Mueve hacia estación de carga; cambia a ‘charging’ si está a <0.5 unidades.
  - En ‘pollinating’: Mueve hacia flor objetivo; poliniza si está a <0.3 unidades.
  - En ‘exploring’: Con probabilidad `exploration_factor`, mueve aleatoriamente (±2 unidades); si no, selecciona flor con ABC.

### 3. Clase `ABCDroneSwarm` (Coordinación del Enjambre)
- **Inicialización**: Crea `Greenhouse` y 15 drones (8 obreros, 4 observadores, 3 exploradores) en posiciones aleatorias. Registra estado inicial (posiciones, estados, métricas).
- **Iteración** (`run_iteration`):
  - Actualiza flores (`update_flowers`).
  - Actualiza cada dron (`update`).
  - Registra estado.
- **Métricas** (`calculate_metrics`): Calcula polinización promedio, energía total, visitas totales.
- **Simulación** (`run_simulation`):
  - Ejecuta 200 iteraciones.
  - Imprime métricas cada 30 iteraciones.
  - Reporta tiempo, polinización promedio, flores bien polinizadas (>80%), visitas.
- **Visualización** (`visualize_simulation`):
  - Usa Matplotlib con `FuncAnimation` para mostrar:
    - Flores (verde, intensidad por polinización, tamaño por madurez).
    - Drones (amarillo: obreros, naranja: observadores, rojo: exploradores; tamaño por batería; etiqueta con estado).
    - Estaciones de carga (cuadrados negros).
    - Métricas en cuadro de texto (polinización, energía, visitas).
  - Guarda animación como `bee_drones_simulation.gif`.
- **Métricas** (`plot_metrics`):
  - Genera cuatro gráficos: polinización promedio, energía total, visitas totales, contribución por tipo de dron (barras).
  - Guarda como `bee_drones_metrics.png`.

### 4. Ejecución Principal
- Configura 8 obreros, 4 observadores, 3 exploradores, 200 iteraciones, invernadero 20x20.
- Crea y ejecuta `ABCDroneSwarm`, genera animación y gráficos.
