import numpy as np
import matplotlib.pyplot as plt
import random
from matplotlib.animation import FuncAnimation
import time

class Greenhouse:
    def __init__(self, width=20, height=20):
        self.width = width
        self.height = height
        self.flowers = []
        self.charging_stations = [
            {'pos': np.array([2, 2]), 'capacity': 3},
            {'pos': np.array([width-3, height-3]), 'capacity': 3},
            {'pos': np.array([width-3, 2]), 'capacity': 2},
            {'pos': np.array([2, height-3]), 'capacity': 2}
        ]
        self.initialize_flowers()
        
    def initialize_flowers(self):
        """Inicializar flores con diferentes niveles de madurez"""
        # Distribuir flores en el invernadero
        n_flowers = 50
        for _ in range(n_flowers):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            maturity = random.choice([1, 2, 3, 4, 5])  # 1: baja, 5: alta prioridad
            pollination_level = 0  # 0-100%
            self.flowers.append({
                'position': np.array([x, y]),
                'maturity': maturity,
                'pollination_level': pollination_level,
                'visits': 0,
                'id': len(self.flowers)  # Añadir un ID único para cada flor
            })
    
    def update_flowers(self):
        """Actualizar estado de las flores (maduración, polinización)"""
        for flower in self.flowers:
            # Las flores maduran con el tiempo (máximo 5)
            if flower['maturity'] < 5 and random.random() < 0.02:
                flower['maturity'] += 1
            
            # La polinización disminuye lentamente si no es visitada
            if flower['pollination_level'] > 0 and random.random() < 0.05:
                flower['pollination_level'] *= 0.98

class BeeDrone:
    def __init__(self, x, y, drone_id, drone_type, greenhouse):
        self.x = x
        self.y = y
        self.id = drone_id
        self.type = drone_type  # 'worker', 'observer', 'scout'
        self.greenhouse = greenhouse
        
        # Estado y energía
        self.battery = 100
        self.energy_consumption_rate = 0.5  # Por unidad de movimiento
        self.charging_rate = 5  # Por iteración de carga
        self.state = 'exploring'  # 'exploring', 'pollinating', 'charging', 'returning'
        
        # Objetivos y memoria
        self.target_flower = None
        self.known_flowers = []  # IDs de flores que conoce este drone
        self.flower_memory = {}  # Memoria de calidad de flores
        self.path = [(x, y)]
        
        # Estadísticas
        self.flowers_pollinated = 0
        self.total_pollination = 0
        self.distance_traveled = 0
        self.charging_time = 0
        
        # Parámetros específicos por tipo
        if self.type == 'worker':
            self.exploration_factor = 0.1
            self.pollination_efficiency = 1.0
        elif self.type == 'observer':
            self.exploration_factor = 0.05
            self.pollination_efficiency = 0.8
        else:  # scout
            self.exploration_factor = 0.3
            self.pollination_efficiency = 0.6
    
    def update_battery(self):
        """Actualizar nivel de batería"""
        if self.state == 'charging':
            self.battery = min(100, self.battery + self.charging_rate)
            self.charging_time += 1
            if self.battery >= 95:
                self.state = 'exploring'
        else:
            # Consumo de energía proporcional a la distancia recorrida
            if len(self.path) > 1:
                last_pos = self.path[-2]
                current_pos = self.path[-1]
                distance = np.sqrt((current_pos[0]-last_pos[0])**2 + (current_pos[1]-last_pos[1])**2)
                self.battery = max(0, self.battery - distance * self.energy_consumption_rate)
            
            # Si la batería es baja, ir a cargar
            if self.battery < 20 and self.state != 'returning':
                self.state = 'returning'
                self.target_flower = None
    
    def find_nearest_charging_station(self):
        """Encontrar la estación de carga más cercana"""
        min_distance = float('inf')
        best_station = None
        
        for station in self.greenhouse.charging_stations:
            distance = np.sqrt((self.x - station['pos'][0])**2 + (self.y - station['pos'][1])**2)
            if distance < min_distance:
                min_distance = distance
                best_station = station
        
        return best_station
    
    def move_toward_target(self, target_x, target_y, speed=0.3):
        """Moverse hacia un objetivo"""
        dx = target_x - self.x
        dy = target_y - self.y
        distance = np.sqrt(dx**2 + dy**2)
        
        if distance > 0:
            # Movimiento normalizado
            self.x += (dx / distance) * speed
            self.y += (dy / distance) * speed
            self.distance_traveled += speed
        
        self.path.append((self.x, self.y))
        return distance
    
    def update_known_flowers(self):
        """Actualizar lista de flores conocidas basado en proximidad"""
        for flower in self.greenhouse.flowers:
            distance = np.sqrt((self.x - flower['position'][0])**2 + 
                             (self.y - flower['position'][1])**2)
            
            # Si está cerca, añadir a flores conocidas (por ID)
            if distance < 3 and flower['id'] not in self.known_flowers:
                self.known_flowers.append(flower['id'])
                
            # Actualizar memoria de calidad de flor
            if flower['id'] in self.known_flowers:
                quality_score = flower['maturity'] * (flower['pollination_level'] / 100)
                self.flower_memory[flower['id']] = quality_score
    
    def get_flower_by_id(self, flower_id):
        """Obtener flor por ID"""
        for flower in self.greenhouse.flowers:
            if flower['id'] == flower_id:
                return flower
        return None
    
    def select_flower_abc(self):
        """Seleccionar flor usando algoritmo ABC"""
        if not self.known_flowers:
            return None
        
        if self.type == 'worker':
            # Abejas obreras: seleccionan basado en calidad conocida
            weights = []
            for flower_id in self.known_flowers:
                flower = self.get_flower_by_id(flower_id)
                if flower is None:
                    continue
                    
                base_weight = self.flower_memory.get(flower_id, flower['maturity'])
                # Penalizar flores muy visitadas
                visit_penalty = max(0, 1 - flower['visits'] * 0.1)
                weight = base_weight * visit_penalty
                weights.append(weight)
            
        elif self.type == 'observer':
            # Abejas observadoras: siguen a las obreras (flores de alta calidad)
            weights = []
            for flower_id in self.known_flowers:
                flower = self.get_flower_by_id(flower_id)
                if flower is None:
                    continue
                    
                base_weight = self.flower_memory.get(flower_id, flower['maturity'])
                # Prefieren flores con alta madurez y baja polinización
                maturity_bonus = flower['maturity'] * 2
                pollination_penalty = max(0.1, 1 - flower['pollination_level'] / 100)
                weight = base_weight * maturity_bonus * pollination_penalty
                weights.append(weight)
                
        else:  # scout
            # Abejas exploradoras: buscan nuevas áreas
            weights = []
            for flower_id in self.known_flowers:
                flower = self.get_flower_by_id(flower_id)
                if flower is None:
                    continue
                    
                # Prefieren flores menos visitadas
                visit_weight = max(0.1, 1 - flower['visits'] * 0.2)
                # Exploración aleatoria
                exploration_bonus = random.uniform(0.5, 1.5)
                weight = visit_weight * exploration_bonus
                weights.append(weight)
        
        # Si no hay pesos válidos, retornar None
        if not weights or sum(weights) == 0:
            return None
            
        # Normalizar pesos
        total_weight = sum(weights)
        if total_weight > 0:
            probabilities = [w / total_weight for w in weights]
            selected_index = np.random.choice(len(self.known_flowers), p=probabilities)
            selected_flower_id = self.known_flowers[selected_index]
            return self.get_flower_by_id(selected_flower_id)
        
        return None
    
    def pollinate_flower(self, flower):
        """Polinizar una flor"""
        if flower['pollination_level'] < 100:
            pollination_amount = self.pollination_efficiency * (5 + flower['maturity'])
            flower['pollination_level'] = min(100, flower['pollination_level'] + pollination_amount)
            flower['visits'] += 1
            
            if flower['pollination_level'] >= 100:
                self.flowers_pollinated += 1
            
            self.total_pollination += pollination_amount
            return True
        return False
    
    def update(self):
        """Actualizar estado del drone"""
        self.update_battery()
        self.update_known_flowers()
        
        # Comportamiento basado en estado
        if self.state == 'returning':
            # Buscar estación de carga
            station = self.find_nearest_charging_station()
            if station:
                distance = self.move_toward_target(station['pos'][0], station['pos'][1])
                if distance < 0.5:  # Llegó a la estación
                    self.state = 'charging'
        
        elif self.state == 'charging':
            # Ya está en modo carga, no hacer nada
            pass
        
        elif self.state == 'pollinating' and self.target_flower:
            # Moverse hacia la flor objetivo
            distance = self.move_toward_target(self.target_flower['position'][0], 
                                             self.target_flower['position'][1])
            
            if distance < 0.3:  # Llegó a la flor
                self.pollinate_flower(self.target_flower)
                self.state = 'exploring'
                self.target_flower = None
        
        else:  # exploring
            # Seleccionar nueva flor o explorar
            if random.random() < self.exploration_factor or not self.known_flowers:
                # Movimiento exploratorio
                target_x = self.x + random.uniform(-2, 2)
                target_y = self.y + random.uniform(-2, 2)
                # Mantener dentro del invernadero
                target_x = max(0, min(self.greenhouse.width, target_x))
                target_y = max(0, min(self.greenhouse.height, target_y))
                self.move_toward_target(target_x, target_y)
            else:
                # Seleccionar flor usando ABC
                self.target_flower = self.select_flower_abc()
                if self.target_flower:
                    self.state = 'pollinating'

class ABCDroneSwarm:
    def __init__(self, n_workers=8, n_observers=4, n_scouts=3, greenhouse_size=20):
        self.greenhouse = Greenhouse(greenhouse_size, greenhouse_size)
        self.drones = []
        self.iteration = 0
        self.history = []
        
        # Crear diferentes tipos de drones
        drone_id = 0
        
        # Abejas obreras
        for _ in range(n_workers):
            x, y = random.uniform(2, greenhouse_size-2), random.uniform(2, greenhouse_size-2)
            drone = BeeDrone(x, y, drone_id, 'worker', self.greenhouse)
            self.drones.append(drone)
            drone_id += 1
        
        # Abejas observadoras
        for _ in range(n_observers):
            x, y = random.uniform(2, greenhouse_size-2), random.uniform(2, greenhouse_size-2)
            drone = BeeDrone(x, y, drone_id, 'observer', self.greenhouse)
            self.drones.append(drone)
            drone_id += 1
        
        # Abejas exploradoras
        for _ in range(n_scouts):
            x, y = random.uniform(2, greenhouse_size-2), random.uniform(2, greenhouse_size-2)
            drone = BeeDrone(x, y, drone_id, 'scout', self.greenhouse)
            self.drones.append(drone)
            drone_id += 1
        
        # Métricas
        self.coverage_history = []
        self.pollination_history = []
        self.energy_history = []
        self.flower_visits_history = []
        
        self.record_state()
    
    def run_iteration(self):
        """Ejecutar una iteración de la simulación"""
        # Actualizar flores
        self.greenhouse.update_flowers()
        
        # Actualizar todos los drones
        for drone in self.drones:
            drone.update()
        
        self.iteration += 1
        self.record_state()
    
    def calculate_metrics(self):
        """Calcular métricas de rendimiento"""
        total_pollination = sum(flower['pollination_level'] for flower in self.greenhouse.flowers)
        avg_pollination = total_pollination / len(self.greenhouse.flowers)
        
        total_energy = sum(drone.battery for drone in self.drones)
        total_flowers_visited = sum(flower['visits'] for flower in self.greenhouse.flowers)
        
        return avg_pollination, total_energy, total_flowers_visited
    
    def record_state(self):
        """Registrar estado actual para visualización"""
        avg_pollination, total_energy, total_visits = self.calculate_metrics()
        
        state = {
            'drones': [{
                'x': drone.x,
                'y': drone.y,
                'type': drone.type,
                'state': drone.state,
                'battery': drone.battery
            } for drone in self.drones],
            'flowers': [flower.copy() for flower in self.greenhouse.flowers],
            'charging_stations': self.greenhouse.charging_stations,
            'avg_pollination': avg_pollination,
            'total_energy': total_energy,
            'total_visits': total_visits
        }
        
        self.history.append(state)
        self.pollination_history.append(avg_pollination)
        self.energy_history.append(total_energy)
        self.flower_visits_history.append(total_visits)
    
    def run_simulation(self, max_iterations=300):
        """Ejecutar simulación completa"""
        start_time = time.time()
        
        for i in range(max_iterations):
            self.run_iteration()
            
            # Mostrar progreso
            if i % 30 == 0:
                avg_poll, energy, visits = self.calculate_metrics()
                print(f"Iteración {i}: Polinización promedio: {avg_poll:.1f}%, "
                      f"Energía total: {energy:.1f}, Visitas: {visits}")
        
        # Métricas finales
        end_time = time.time()
        simulation_time = end_time - start_time
        
        avg_pollination, total_energy, total_visits = self.calculate_metrics()
        total_pollinated = sum(1 for f in self.greenhouse.flowers if f['pollination_level'] >= 80)
        
        print("\n--- SIMULACIÓN COMPLETADA ---")
        print(f"Tiempo: {simulation_time:.2f}s, Iteraciones: {self.iteration}")
        print(f"Polinización promedio: {avg_pollination:.1f}%")
        print(f"Flores bien polinizadas (>80%): {total_pollinated}/{len(self.greenhouse.flowers)}")
        print(f"Visitas totales a flores: {total_visits}")
        
        return avg_pollination, total_energy, simulation_time
    
    def visualize_simulation(self):
        """Visualizar la simulación"""
        fig, ax = plt.subplots(figsize=(12, 10))
        
        # Colores por tipo de drone
        drone_colors = {
            'worker': 'yellow',
            'observer': 'orange', 
            'scout': 'red'
        }
        
        def update(frame):
            state = self.history[frame]
            
            # Limpiar
            ax.clear()
            
            # Dibujar flores (color por nivel de polinización)
            for flower in state['flowers']:
                color_intensity = flower['pollination_level'] / 100
                color = (0, color_intensity, 0)  # Verde más intenso = más polinizada
                size = 30 + flower['maturity'] * 10  # Tamaño por madurez
                
                ax.scatter(flower['position'][0], flower['position'][1], 
                          c=[color], s=size, alpha=0.7, edgecolors='darkgreen')
            
            # Dibujar estaciones de carga
            for station in state['charging_stations']:
                ax.plot(station['pos'][0], station['pos'][1], 'ks', 
                       markersize=15, label='Estación de carga')
            
            # Dibujar drones
            for drone in state['drones']:
                # Color base por tipo
                base_color = drone_colors[drone['type']]
                
                # Tamaño por batería
                size = 50 + drone['battery'] * 0.5
                
                ax.scatter(drone['x'], drone['y'], c=base_color, s=size, 
                          edgecolors='black', linewidth=1, alpha=0.8)
                
                # Añadir etiqueta de estado
                ax.text(drone['x'], drone['y'] + 0.3, drone['state'][0], 
                       ha='center', va='center', fontsize=8, fontweight='bold')
            
            # Configuración del gráfico
            ax.set_xlim(0, self.greenhouse.width)
            ax.set_ylim(0, self.greenhouse.height)
            ax.set_xlabel('Coordenada X')
            ax.set_ylabel('Coordenada Y')
            ax.set_title(f'Polinización con Drones-Abejas - Iteración {frame}')
            ax.grid(True, alpha=0.3)
            
            # Leyenda
            from matplotlib.patches import Patch
            legend_elements = [
                Patch(facecolor='yellow', label='Obreras'),
                Patch(facecolor='orange', label='Observadoras'),
                Patch(facecolor='red', label='Exploradoras'),
                plt.Line2D([0], [0], marker='s', color='k', label='Estación carga', 
                          markersize=8, linestyle='None')
            ]
            ax.legend(handles=legend_elements, loc='upper right')
            
            # Información de estado
            info_text = (f'Polinización promedio: {state["avg_pollination"]:.1f}%\n'
                        f'Energía total: {state["total_energy"]:.1f}\n'
                        f'Visitas totales: {state["total_visits"]}')
            ax.text(0.02, 0.98, info_text, transform=ax.transAxes, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            return ax,
        
        ani = FuncAnimation(fig, update, frames=len(self.history), interval=200, repeat=False)
        
        # Guardar animación
        try:
            ani.save('bee_drones_simulation.gif', writer='pillow', fps=5)
            print("Animación guardada como 'bee_drones_simulation.gif'")
        except Exception as e:
            print(f"No se pudo guardar la animación: {e}")
        
        plt.tight_layout()
        plt.show()
        
        # Mostrar métricas
        self.plot_metrics()
    
    def plot_metrics(self):
        """Graficar métricas de la simulación"""
        fig, axes = plt.subplots(2, 2, figsize=(12, 10))
        
        # Polinización vs Iteraciones
        axes[0,0].plot(self.pollination_history)
        axes[0,0].set_xlabel('Iteración')
        axes[0,0].set_ylabel('Polinización Promedio (%)')
        axes[0,0].set_title('Evolución de la Polinización')
        axes[0,0].grid(True)
        
        # Energía vs Iteraciones
        axes[0,1].plot(self.energy_history)
        axes[0,1].set_xlabel('Iteración')
        axes[0,1].set_ylabel('Energía Total')
        axes[0,1].set_title('Energía de la Colmena')
        axes[0,1].grid(True)
        
        # Visitas vs Iteraciones
        axes[1,0].plot(self.flower_visits_history)
        axes[1,0].set_xlabel('Iteración')
        axes[1,0].set_ylabel('Visitas Totales')
        axes[1,0].set_title('Visitas a Flores')
        axes[1,0].grid(True)
        
        # Distribución de trabajo por tipo de drone
        worker_pollination = sum(d.flowers_pollinated for d in self.drones if d.type == 'worker')
        observer_pollination = sum(d.flowers_pollinated for d in self.drones if d.type == 'observer')
        scout_pollination = sum(d.flowers_pollinated for d in self.drones if d.type == 'scout')
        
        types = ['Obreras', 'Observadoras', 'Exploradoras']
        pollination = [worker_pollination, observer_pollination, scout_pollination]
        
        axes[1,1].bar(types, pollination, color=['yellow', 'orange', 'red'])
        axes[1,1].set_ylabel('Flores Polinizadas')
        axes[1,1].set_title('Contribución por Tipo de Drone')
        
        # Añadir valores en las barras
        for i, v in enumerate(pollination):
            axes[1,1].text(i, v + 0.1, str(v), ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig('bee_drones_metrics.png', dpi=300)
        plt.show()

# Ejecutar la simulación
if __name__ == "__main__":
    # Configuración
    n_workers = 8
    n_observers = 4  
    n_scouts = 3
    max_iterations = 200
    
    # Crear y ejecutar simulación
    swarm = ABCDroneSwarm(
        n_workers=n_workers,
        n_observers=n_observers, 
        n_scouts=n_scouts,
        greenhouse_size=20
    )
    
    # Ejecutar simulación
    avg_pollination, total_energy, sim_time = swarm.run_simulation(max_iterations)
    
    # Visualizar resultados
    swarm.visualize_simulation()