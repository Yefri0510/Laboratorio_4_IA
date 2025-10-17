import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random

class AdvancedDroneFormationPSO:
    def __init__(self, n_drones=15, max_iter=60, formation_type='dragon'):
        # Configuración del espacio aéreo
        self.bounds = [-8, 8]
        self.n_drones = n_drones
        self.max_iter = max_iter
        self.formation_type = formation_type
        
        # La formación objetivo (seleccionable)
        self.target_formation = self.create_formation(formation_type, radius=3, center=[0, 0])
        
        # Obstáculos a evitar
        self.obstacles = [
            {'center': np.array([-2, 1]), 'radius': 1.2},
            {'center': np.array([3, -2]), 'radius': 1.5},
            {'center': np.array([0, -3]), 'radius': 1.0}
        ]
        
        # Inicializar los drones en posiciones aleatorias
        self.drones = np.random.uniform(self.bounds[0], self.bounds[1], 
                                       (self.n_drones, 2))
        self.velocities = np.zeros((self.n_drones, 2))
        
        # Tolerancia a fallos - DEFINIR ESTO ANTES de fitness
        self.active_drones = [True] * self.n_drones
        self.failure_iteration = None
        
        # Mejores posiciones personales y globales
        self.personal_best = self.drones.copy()
        self.personal_best_fitness = np.array([self.fitness(p, i) for i, p in enumerate(self.drones)])
        self.global_best = self.drones[np.argmin(self.personal_best_fitness)]
        self.global_best_fitness = np.min(self.personal_best_fitness)
        
        # Historial para la animación
        self.history = [self.drones.copy()]
        
    def create_formation(self, formation_type, radius, center, n_points=15):
        """Crear diferentes formaciones de drones"""
        angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        formation = []
        
        if formation_type == 'circle':
            # Formación circular (ya existente)
            for angle in angles:
                x = center[0] + radius * np.cos(angle)
                y = center[1] + radius * np.sin(angle)
                formation.append(np.array([x, y]))
                
        elif formation_type == 'dragon':
            # Formación de dragón (silueta simplificada)
            for i, angle in enumerate(angles):
                # Crear una forma de dragón usando una combinación de senos y cosenos
                t = angle
                scale = 0.8
                x = center[0] + radius * scale * (np.cos(t) + 0.5 * np.cos(3*t) + 0.25 * np.sin(5*t))
                y = center[1] + radius * scale * (np.sin(t) + 0.5 * np.sin(3*t) + 0.25 * np.cos(5*t))
                formation.append(np.array([x, y]))
                
        elif formation_type == 'robot':
            # Formación de robot (silueta simplificada)
            for i, angle in enumerate(angles):
                # Crear una forma de robot con partes rectangulares y circulares
                t = angle
                if i < n_points//3:
                    # Cabeza (semicírculo superior)
                    x = center[0] + radius * 0.7 * np.cos(t * 1.5)
                    y = center[1] + radius * 0.7 * np.sin(t * 1.5) + radius * 0.5
                elif i < 2*n_points//3:
                    # Cuerpo (rectángulo con esquinas redondeadas)
                    segment = (i - n_points//3) / (n_points//3)
                    x = center[0] + radius * (0.8 * np.cos(np.pi * segment) - 0.1)
                    y = center[1] + radius * (0.3 * np.sin(np.pi * segment) - 0.2)
                else:
                    # Piernas (dos rectángulos)
                    segment = (i - 2*n_points//3) / (n_points//3)
                    x = center[0] + radius * (0.3 * np.cos(np.pi * segment) - 0.4 if i % 2 == 0 else 0.3 * np.cos(np.pi * segment) + 0.4)
                    y = center[1] + radius * (0.5 * np.sin(np.pi * segment) - 0.8)
                formation.append(np.array([x, y]))
                
        elif formation_type == 'star':
            # Formación de estrella
            for i, angle in enumerate(angles):
                # Crear una estrella de 5 puntas
                t = angle
                # Alternar entre radio grande y pequeño para crear puntas
                r = radius * (0.5 + 0.5 * (i % 2)) if i % 2 == 0 else radius * 0.3
                x = center[0] + r * np.cos(t)
                y = center[1] + r * np.sin(t)
                formation.append(np.array([x, y]))
        
        return formation
    
    def simulate_failure(self, iteration):
        """Simular fallo de un dron en una iteración específica"""
        if iteration == self.max_iter // 2 and self.failure_iteration is None:
            # Seleccionar un dron aleatorio para fallar (excepto el mejor)
            active_indices = [i for i, active in enumerate(self.active_drones) if active]
            if len(active_indices) > 1:  # Asegurar que hay al menos 2 drones activos
                failed_drone = random.choice([i for i in active_indices if i != np.argmin(self.personal_best_fitness)])
                self.active_drones[failed_drone] = False
                self.failure_iteration = iteration
                print(f"¡Dron {failed_drone} ha fallado en la iteración {iteration}!")
                
                # Recalcular la formación objetivo sin el dron fallido
                active_count = sum(self.active_drones)
                self.target_formation = self.create_formation(
                    self.formation_type, radius=3, center=[0, 0], n_points=active_count
                )
    
    def fitness(self, position, drone_idx):
        """Función de aptitud mejorada: qué tan buena es una posición para un drone"""
        if not self.active_drones[drone_idx]:
            return float('inf')  # Penalización infinita para drones inactivos
            
        # 1. Distancia a la posición objetivo en la formación
        # Si hay drones inactivos, redistribuir los objetivos entre los activos
        active_indices = [i for i, active in enumerate(self.active_drones) if active]
        target_idx = active_indices.index(drone_idx) if drone_idx in active_indices else 0
        if target_idx < len(self.target_formation):
            target_pos = self.target_formation[target_idx]
        else:
            target_pos = self.target_formation[0]  # Fallback
            
        distance_to_target = np.sqrt(np.sum((position - target_pos)**2))
        
        # 2. Penalización por acercarse a obstáculos
        obstacle_penalty = 0
        for obstacle in self.obstacles:
            distance_to_obstacle = np.sqrt(np.sum((position - obstacle['center'])**2))
            if distance_to_obstacle < obstacle['radius']:
                # Gran penalización si está dentro del obstáculo
                obstacle_penalty += 100
            else:
                # Penalización menor si está cerca pero no dentro
                obstacle_penalty += max(0, 1/(distance_to_obstacle - obstacle['radius']) - 1)
        
        # 3. Penalización por colisionar con otros drones
        collision_penalty = 0
        for i, other_drone in enumerate(self.drones):
            if i != drone_idx and self.active_drones[i]:
                distance = np.sqrt(np.sum((position - other_drone)**2))
                if distance < 0.5:  # Distancia mínima segura entre drones
                    collision_penalty += 10 * (0.5 - distance)
        
        # 4. Penalización por movimientos bruscos (optimización de energía)
        energy_penalty = 0.1 * np.sqrt(np.sum(self.velocities[drone_idx]**2))
        
        return distance_to_target + obstacle_penalty + collision_penalty + energy_penalty
    
    def navigate(self):
        """Los drones navegan para formar la figura con tolerancia a fallos"""
        for iteration in range(self.max_iter):
            # Simular fallo de un dron en la mitad de las iteraciones
            self.simulate_failure(iteration)
            
            for i in range(self.n_drones):
                if not self.active_drones[i]:
                    continue  # Saltar drones inactivos
                    
                # Factores aleatorios para la exploración
                r1, r2 = np.random.rand(2)
                
                # Componentes de la velocidad:
                inertia = 0.8 * self.velocities[i]
                memory = 1.5 * r1 * (self.personal_best[i] - self.drones[i])
                social = 1.5 * r2 * (self.global_best - self.drones[i])
                
                # Actualizar velocidad y posición
                self.velocities[i] = inertia + memory + social
                self.drones[i] += self.velocities[i]
                
                # Mantener a los drones dentro del espacio aéreo
                self.drones[i] = np.clip(self.drones[i], self.bounds[0], self.bounds[1])
                
                # Evaluar la nueva posición
                current_fitness = self.fitness(self.drones[i], i)
                
                # Actualizar mejores posiciones (minimizando)
                if current_fitness < self.personal_best_fitness[i]:
                    self.personal_best[i] = self.drones[i]
                    self.personal_best_fitness[i] = current_fitness
                    
                    if current_fitness < self.global_best_fitness:
                        self.global_best = self.drones[i]
                        self.global_best_fitness = current_fitness
            
            # Guardar posición para la animación
            self.history.append(self.drones.copy())
            
            if (iteration + 1) % 10 == 0:
                active_count = sum(self.active_drones)
                print(f"Iteración {iteration+1}: Mejor aptitud = {self.global_best_fitness:.3f}, Drones activos: {active_count}/{self.n_drones}")
        
        return self.global_best, self.global_best_fitness
    
    def visualize_navigation(self):
        """Visualizar la navegación de los drones"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Dibujar los obstáculos
        for obstacle in self.obstacles:
            circle = plt.Circle(obstacle['center'], obstacle['radius'], 
                               color='red', alpha=0.3, label='Obstáculos' if obstacle is self.obstacles[0] else "")
            ax.add_patch(circle)
        
        # Dibujar la formación objetivo
        target_x = [pos[0] for pos in self.target_formation]
        target_y = [pos[1] for pos in self.target_formation]
        ax.plot(target_x, target_y, 'go', markersize=8, label='Formación objetivo')
        
        # Inicializar los drones
        drones_plot = ax.scatter([], [], c='blue', edgecolors='black', 
                                s=50, label='Drones activos')
        inactive_drones_plot = ax.scatter([], [], c='gray', edgecolors='black', 
                                         s=50, label='Drones inactivos')
        best_drone_plot = ax.scatter([], [], c='red', edgecolors='black', 
                                    s=100, label='Mejor posición')
        
        ax.set_xlim(self.bounds)
        ax.set_ylim(self.bounds)
        ax.set_xlabel('Coordenada X')
        ax.set_ylabel('Coordenada Y')
        ax.set_title(f'Navegación de Drones en Formación {self.formation_type.capitalize()} con PSO')
        ax.legend()
        ax.grid(True)
        
        def update(frame):
            drones = self.history[frame]
            active_drones_pos = []
            inactive_drones_pos = []
            
            for i, drone in enumerate(drones):
                if i < len(self.active_drones) and self.active_drones[i]:
                    active_drones_pos.append(drone)
                else:
                    inactive_drones_pos.append(drone)
            
            # Actualizar drones activos
            if active_drones_pos:
                drones_plot.set_offsets(active_drones_pos)
            else:
                drones_plot.set_offsets([])
                
            # Actualizar drones inactivos
            if inactive_drones_pos:
                inactive_drones_plot.set_offsets(inactive_drones_pos)
            else:
                inactive_drones_plot.set_offsets([])
            
            # Encontrar el drone activo con mejor aptitud en este frame
            best_pos = None
            best_fitness = float('inf')
            for i, drone in enumerate(drones):
                if i < len(self.active_drones) and self.active_drones[i]:
                    # Para evitar cálculos costosos, usamos una aproximación simple
                    # En una implementación real, podríamos precalcular esto
                    target_idx = [j for j, active in enumerate(self.active_drones) if active].index(i)
                    if target_idx < len(self.target_formation):
                        target_pos = self.target_formation[target_idx]
                        fitness_val = np.sqrt(np.sum((drone - target_pos)**2))
                        if fitness_val < best_fitness:
                            best_fitness = fitness_val
                            best_pos = drone
            
            if best_pos is not None:
                best_drone_plot.set_offsets([best_pos])
            else:
                best_drone_plot.set_offsets([])
            
            return drones_plot, inactive_drones_plot, best_drone_plot
        
        ani = FuncAnimation(fig, update, frames=len(self.history), 
                           interval=200, blit=True, repeat=False)
        
        # Guardar la animación como archivo GIF
        try:
            filename = f'drones_{self.formation_type}_animation.gif'
            ani.save(filename, writer='pillow', fps=5)
            print(f"Animación guardada como '{filename}'")
        except Exception as e:
            print(f"No se pudo guardar la animación: {e}")
        
        # Mostrar la animación
        plt.show()

# Ejecutar la navegación de drones para las tres formaciones
formations = ['dragon', 'robot', 'star']

for formation in formations:
    print(f"\n=== Ejecutando formación {formation} ===")
    drone_formation = AdvancedDroneFormationPSO(n_drones=15, max_iter=40, formation_type=formation)
    best_position, best_fitness = drone_formation.navigate()
    
    print(f"¡Mejor posición encontrada: {best_position}")
    print(f"Aptitud de la mejor posición: {best_fitness:.3f}")
    
    # Mostrar la animación
    drone_formation.visualize_navigation()