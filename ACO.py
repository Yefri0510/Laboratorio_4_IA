import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation
import time

class DisasterZone:
    def __init__(self, width=30, height=30):
        self.width = width
        self.height = height
        self.grid = np.zeros((height, width))  # 0: terreno libre, 1: obstáculo, 2: superviviente, 3: recurso
        self.pheromone_grid = np.zeros((height, width))  # Rastro de feromonas
        self.visited_grid = np.zeros((height, width))  # Registro de celdas visitadas
        self.survivors_found = 0
        self.total_survivors = 0
        self.initialize_zone()
        
    def initialize_zone(self):
        # Agregar obstáculos (escombros)
        for _ in range(40):
            x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
            size = random.randint(1, 3)
            for i in range(max(0, x-size), min(self.width, x+size+1)):
                for j in range(max(0, y-size), min(self.height, y+size+1)):
                    if random.random() < 0.7:
                        self.grid[j, i] = 1
        
        # Agregar supervivientes
        for _ in range(15):
            while True:
                x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
                if self.grid[y, x] == 0:  # Solo en terreno libre
                    self.grid[y, x] = 2
                    self.total_survivors += 1
                    break
        
        # Agregar recursos
        for _ in range(10):
            while True:
                x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
                if self.grid[y, x] == 0:  # Solo en terreno libre
                    self.grid[y, x] = 3
                    break
    
    def add_dynamic_obstacle(self):
        """Añadir un obstáculo dinámico (nuevos escombros)"""
        x, y = random.randint(0, self.width-1), random.randint(0, self.height-1)
        size = random.randint(2, 4)
        for i in range(max(0, x-size), min(self.width, x+size+1)):
            for j in range(max(0, y-size), min(self.height, y+size+1)):
                if random.random() < 0.6 and self.grid[j, i] == 0:
                    self.grid[j, i] = 1
        return (x, y, size)
    
    def evaporate_pheromones(self, evaporation_rate=0.1):
        """Evaporar feromonas con el tiempo"""
        self.pheromone_grid *= (1 - evaporation_rate)
    
    def deposit_pheromone(self, x, y, amount):
        """Depositar feromonas en una posición"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pheromone_grid[y, x] += amount
    
    def mark_visited(self, x, y):
        """Marcar una celda como visitada"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.visited_grid[y, x] = 1
    
    def get_coverage_percentage(self):
        """Calcular el porcentaje del área cubierta"""
        total_cells = self.width * self.height
        obstacle_cells = np.sum(self.grid == 1)
        accessible_cells = total_cells - obstacle_cells
        visited_cells = np.sum(self.visited_grid == 1)
        
        if accessible_cells > 0:
            return (visited_cells / accessible_cells) * 100
        return 0

class AntDrone:
    def __init__(self, x, y, drone_id, zone):
        self.x = x
        self.y = y
        self.id = drone_id
        self.zone = zone
        self.path = [(x, y)]
        self.survivors_found = 0
        self.resources_found = 0
        self.energy_consumed = 0
        self.pheromone_strength = 10  # Cantidad de feromona a depositar
        self.has_target = False
        self.target_position = None
        
    def move(self, alpha=1, beta=2, exploration_factor=0.1):
        """Mover el drone basado en el algoritmo ACO"""
        # Si tiene un objetivo, moverse hacia él
        if self.has_target and self.target_position:
            self.move_toward_target()
            return
        
        # Obtener vecinos válidos
        neighbors = self.get_valid_neighbors()
        
        if not neighbors:
            return  # No hay movimientos posibles
        
        # Calcular probabilidades para cada vecino
        probabilities = []
        for nx, ny in neighbors:
            # Feromonas en la celda vecina
            pheromone = self.zone.pheromone_grid[ny, nx] + 0.1  # Evitar división por cero
            
            # Heurística: preferir celdas no visitadas y con recursos/supervivientes
            heuristic = 1.0
            if self.zone.visited_grid[ny, nx] == 0:
                heuristic *= 2  # Preferir celdas no visitadas
            
            cell_type = self.zone.grid[ny, nx]
            if cell_type == 2:  # Superviviente
                heuristic *= 5
            elif cell_type == 3:  # Recurso
                heuristic *= 3
            
            # Factor de exploración aleatoria
            if random.random() < exploration_factor:
                heuristic *= random.uniform(1, 3)
            
            # Calcular probabilidad
            probability = (pheromone ** alpha) * (heuristic ** beta)
            probabilities.append(probability)
        
        # Normalizar probabilidades
        total = sum(probabilities)
        if total > 0:
            probabilities = [p / total for p in probabilities]
        else:
            # Si todas las probabilidades son cero, usar distribución uniforme
            probabilities = [1 / len(neighbors)] * len(neighbors)
        
        # Seleccionar movimiento basado en probabilidades
        next_index = np.random.choice(len(neighbors), p=probabilities)
        next_x, next_y = neighbors[next_index]
        
        # Actualizar posición
        self.x, self.y = next_x, next_y
        self.path.append((self.x, self.y))
        self.energy_consumed += 1
        
        # Marcar celda como visitada
        self.zone.mark_visited(self.x, self.y)
        
        # Depositar feromonas
        self.zone.deposit_pheromone(self.x, self.y, self.pheromone_strength)
        
        # Verificar si encontró algo
        self.check_cell_content()
    
    def move_toward_target(self):
        """Moverse hacia el objetivo actual"""
        if not self.target_position:
            self.has_target = False
            return
        
        tx, ty = self.target_position
        
        # Calcular dirección hacia el objetivo
        dx = tx - self.x
        dy = ty - self.y
        
        # Normalizar dirección (moverse un paso hacia el objetivo)
        if abs(dx) > abs(dy):
            next_x = self.x + (1 if dx > 0 else -1)
            next_y = self.y
        else:
            next_x = self.x
            next_y = self.y + (1 if dy > 0 else -1)
        
        # Verificar si el movimiento es válido
        if (0 <= next_x < self.zone.width and 0 <= next_y < self.zone.height and 
            self.zone.grid[next_y, next_x] != 1):  # No es un obstáculo
            self.x, self.y = next_x, next_y
        else:
            # Si el movimiento directo no es posible, buscar ruta alternativa
            neighbors = self.get_valid_neighbors()
            if neighbors:
                # Elegir el vecino más cercano al objetivo
                min_dist = float('inf')
                best_neighbor = neighbors[0]
                for nx, ny in neighbors:
                    dist = abs(nx - tx) + abs(ny - ty)  # Distancia Manhattan
                    if dist < min_dist:
                        min_dist = dist
                        best_neighbor = (nx, ny)
                self.x, self.y = best_neighbor
        
        self.path.append((self.x, self.y))
        self.energy_consumed += 1
        self.zone.mark_visited(self.x, self.y)
        self.zone.deposit_pheromone(self.x, self.y, self.pheromone_strength)
        
        # Verificar si llegó al objetivo
        if (self.x, self.y) == self.target_position:
            self.has_target = False
            self.target_position = None
        
        # Verificar si encontró algo
        self.check_cell_content()
    
    def get_valid_neighbors(self):
        """Obtener vecinos válidos para moverse"""
        neighbors = []
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                # Excluir la posición actual
                if dx == 0 and dy == 0:
                    continue
                
                nx, ny = self.x + dx, self.y + dy
                
                # Verificar límites y obstáculos
                if (0 <= nx < self.zone.width and 0 <= ny < self.zone.height and 
                    self.zone.grid[ny, nx] != 1):  # No es un obstáculo
                    neighbors.append((nx, ny))
        
        return neighbors
    
    def check_cell_content(self):
        """Verificar el contenido de la celda actual"""
        cell_type = self.zone.grid[self.y, self.x]
        
        if cell_type == 2:  # Superviviente
            self.survivors_found += 1
            self.zone.survivors_found += 1
            self.zone.grid[self.y, self.x] = 0  # Remover superviviente
            # Depositar feromonas extra por encontrar superviviente
            self.zone.deposit_pheromone(self.x, self.y, self.pheromone_strength * 5)
            print(f"¡Drone {self.id} encontró un superviviente! Total: {self.zone.survivors_found}/{self.zone.total_survivors}")
        
        elif cell_type == 3:  # Recurso
            self.resources_found += 1
            self.zone.grid[self.y, self.x] = 0  # Remover recurso
            # Depositar feromonas extra por encontrar recurso
            self.zone.deposit_pheromone(self.x, self.y, self.pheromone_strength * 3)
    
    def set_target(self, x, y):
        """Establecer un objetivo específico para el drone"""
        self.has_target = True
        self.target_position = (x, y)

class ACODroneSwarm:
    def __init__(self, n_drones=10, zone_width=30, zone_height=30):
        self.zone = DisasterZone(zone_width, zone_height)
        self.n_drones = n_drones
        self.drones = []
        self.iteration = 0
        self.history = []
        self.coverage_history = []
        self.energy_history = []
        self.survivors_history = []
        
        # Inicializar drones en posiciones aleatorias
        for i in range(n_drones):
            while True:
                x, y = random.randint(0, zone_width-1), random.randint(0, zone_height-1)
                if self.zone.grid[y, x] == 0:  # Posición libre
                    drone = AntDrone(x, y, i, self.zone)
                    self.drones.append(drone)
                    break
        
        # Registrar estado inicial
        self.record_state()
    
    def run_iteration(self, alpha=1, beta=2, exploration_factor=0.1):
        """Ejecutar una iteración del algoritmo ACO"""
        # Evaporar feromonas
        self.zone.evaporate_pheromones()
        
        # Mover todos los drones
        for drone in self.drones:
            drone.move(alpha, beta, exploration_factor)
        
        # Ocasionalmente agregar un obstáculo dinámico (cada 20 iteraciones)
        if self.iteration % 20 == 10 and self.iteration > 0:
            obstacle_pos = self.zone.add_dynamic_obstacle()
            print(f"Iteración {self.iteration}: Se añadió un nuevo obstáculo en {obstacle_pos}")
        
        # Ocasionalmente asignar objetivos a drones ociosos (cada 15 iteraciones)
        if self.iteration % 15 == 0 and self.iteration > 0:
            self.assign_targets()
        
        self.iteration += 1
        self.record_state()
    
    def assign_targets(self):
        """Asignar objetivos a drones basado en feromonas"""
        # Encontrar celdas con alta concentración de feromonas
        high_pheromone_threshold = np.percentile(self.zone.pheromone_grid, 80)
        high_pheromone_cells = np.argwhere(self.zone.pheromone_grid >= high_pheromone_threshold)
        
        # Asignar estos objetivos a drones que no tienen objetivo
        idle_drones = [drone for drone in self.drones if not drone.has_target]
        
        for drone in idle_drones[:min(len(high_pheromone_cells), len(idle_drones))]:
            target_idx = random.randint(0, len(high_pheromone_cells) - 1)
            ty, tx = high_pheromone_cells[target_idx]
            drone.set_target(tx, ty)
    
    def record_state(self):
        """Registrar el estado actual para visualización"""
        # Crear una copia del estado actual
        state = {
            'drones': [(drone.x, drone.y) for drone in self.drones],
            'visited': self.zone.visited_grid.copy(),
            'grid': self.zone.grid.copy(),
            'coverage': self.zone.get_coverage_percentage(),
            'total_energy': sum(drone.energy_consumed for drone in self.drones),
            'survivors_found': self.zone.survivors_found
        }
        self.history.append(state)
        self.coverage_history.append(state['coverage'])
        self.energy_history.append(state['total_energy'])
        self.survivors_history.append(state['survivors_found'])
    
    def run_simulation(self, max_iterations=200, alpha=1, beta=2, exploration_factor=0.1):
        """Ejecutar la simulación completa"""
        start_time = time.time()
        
        for i in range(max_iterations):
            self.run_iteration(alpha, beta, exploration_factor)
            
            # Mostrar progreso cada 20 iteraciones
            if i % 20 == 0:
                coverage = self.zone.get_coverage_percentage()
                survivors = self.zone.survivors_found
                energy = sum(drone.energy_consumed for drone in self.drones)
                print(f"Iteración {i}: Cobertura {coverage:.1f}%, Supervivientes {survivors}/{self.zone.total_survivors}, Energía {energy}")
            
            # Detener si se encontraron todos los supervivientes
            if self.zone.survivors_found >= self.zone.total_survivors:
                print(f"¡Todos los supervivientes encontrados en la iteración {i}!")
                break
        
        end_time = time.time()
        simulation_time = end_time - start_time
        
        # Métricas finales
        final_coverage = self.zone.get_coverage_percentage()
        total_energy = sum(drone.energy_consumed for drone in self.drones)
        
        print("\n--- SIMULACIÓN COMPLETADA ---")
        print(f"Tiempo de simulación: {simulation_time:.2f} segundos")
        print(f"Iteraciones: {self.iteration}")
        print(f"Cobertura final: {final_coverage:.2f}%")
        print(f"Supervivientes encontrados: {self.zone.survivors_found}/{self.zone.total_survivors}")
        print(f"Energía total consumida: {total_energy}")
        
        return final_coverage, total_energy, simulation_time
    
    def visualize_simulation(self):
        """Visualizar la simulación completa sin mapa de feromonas"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Configurar colores para el terreno
        terrain_cmap = plt.cm.colors.ListedColormap(['white', 'black', 'green', 'blue'])
        terrain_bounds = [0, 1, 2, 3, 4]
        terrain_norm = plt.cm.colors.BoundaryNorm(terrain_bounds, terrain_cmap.N)
        
        def update(frame):
            state = self.history[frame]
            
            # Limpiar el eje
            ax.clear()
            
            # Mostrar el terreno
            ax.imshow(state['grid'], cmap=terrain_cmap, norm=terrain_norm, alpha=0.7)
            
            # Agregar drones
            drone_x = [pos[0] for pos in state['drones']]
            drone_y = [pos[1] for pos in state['drones']]
            ax.scatter(drone_x, drone_y, c='red', s=50, edgecolors='black', label='Drones')
            
            # Mostrar áreas visitadas (transparentes)
            visited_mask = state['visited'] == 1
            if np.any(visited_mask):
                y_coords, x_coords = np.where(visited_mask)
                ax.scatter(x_coords, y_coords, c='yellow', alpha=0.2, s=10, label='Áreas visitadas')
            
            # Configurar el gráfico
            ax.set_title(f'Búsqueda de Supervivientes - Iteración {frame}')
            ax.set_xlabel('Coordenada X')
            ax.set_ylabel('Coordenada Y')
            ax.legend()
            
            # Información de estado
            coverage = state['coverage']
            survivors = state['survivors_found']
            energy = state['total_energy']
            
            # Añadir texto con métricas
            ax.text(0.02, 0.98, f'Cobertura: {coverage:.1f}%\nSupervivientes: {survivors}/{self.zone.total_survivors}\nEnergía: {energy}', 
                   transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            return ax,
        
        ani = FuncAnimation(fig, update, frames=len(self.history), interval=200, repeat=False)
        
        # Guardar animación
        try:
            ani.save('drones_ant_simulation.gif', writer='pillow', fps=5)
            print("Animación guardada como 'drones_ant_simulation.gif'")
        except Exception as e:
            print(f"No se pudo guardar la animación: {e}")
        
        plt.tight_layout()
        plt.show()
        
        # Mostrar métricas finales
        self.plot_metrics()
    
    def plot_metrics(self):
        """Graficar métricas de la simulación"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # Cobertura vs Iteraciones
        axes[0].plot(self.coverage_history)
        axes[0].set_xlabel('Iteración')
        axes[0].set_ylabel('Cobertura (%)')
        axes[0].set_title('Cobertura del Área vs Tiempo')
        axes[0].grid(True)
        
        # Energía vs Iteraciones
        axes[1].plot(self.energy_history)
        axes[1].set_xlabel('Iteración')
        axes[1].set_ylabel('Energía Consumida')
        axes[1].set_title('Energía Total vs Tiempo')
        axes[1].grid(True)
        
        # Supervivientes vs Iteraciones
        axes[2].plot(self.survivors_history)
        axes[2].set_xlabel('Iteración')
        axes[2].set_ylabel('Supervivientes Encontrados')
        axes[2].set_title('Supervivientes Rescatados vs Tiempo')
        axes[2].grid(True)
        
        plt.tight_layout()
        plt.savefig('drones_ant_metrics.png', dpi=300)
        plt.show()

# Ejecutar la simulación
if __name__ == "__main__":
    # Parámetros de la simulación
    n_drones = 12
    zone_size = 30
    max_iterations = 150
    
    # Crear y ejecutar simulación
    swarm = ACODroneSwarm(n_drones=n_drones, zone_width=zone_size, zone_height=zone_size)
    
    # Ejecutar simulación con parámetros ACO
    final_coverage, total_energy, sim_time = swarm.run_simulation(
        max_iterations=max_iterations,
        alpha=1,        # Peso de las feromonas
        beta=2,         # Peso de la heurística
        exploration_factor=0.1  # Factor de exploración aleatoria
    )
    
    # Visualizar resultados
    swarm.visualize_simulation()