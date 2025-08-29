import sys, os, math
from typing import Optional
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from base_agent import BaseAgent

class Position:
    def __init__(self, x: int = 0, y: int = 0):
        self.x: int = x
        self.y: int = y

    def __eq__(self, other) -> bool:
        if not isinstance(other, Position):
            return False
        return self.x == other.x and self.y == other.y
    
    def __add__(self, other): return Position(self.x + other.x, self.y + other.y)
    def __sub__(self, other): return Position(self.x - other.x, self.y - other.y)
    def __mul__(self, k): return Position(self.x * k, self.y * k)
    __rmul__ = __mul__

Section = Position

class Perception:
    def __init__(self, pos: Position = None, is_dirty: bool = False, actions_remaining: int = 0, 
                 actions_consumed: int = 0, cells_cleaned: int = 0, is_finished: bool = False):
        self.pos: Position = pos if pos is not None else Position()
        self.is_dirty: bool = is_dirty
        self.actions_remaining: int = actions_remaining
        self.actions_consumed: int = actions_consumed
        self.cells_cleaned: int = cells_cleaned
        self.is_finished: bool = is_finished

class ReflexAgent(BaseAgent):
    
    def __init__(self, server_url: str = "http://localhost:5000", 
                 enable_ui: bool = False,
                 record_game: bool = False, 
                 replay_file: Optional[str] = None,
                 cell_size: int = 60,
                 fps: int = 10,
                 auto_exit_on_finish: bool = True,
                 live_stats: bool = False):
        super().__init__(server_url, "ReflexAgent", enable_ui, record_game, 
                        replay_file, cell_size, fps, auto_exit_on_finish, live_stats)
        
    def get_strategy_description(self) -> str:
        return "Recorre la grilla de manera recursiva, siguiendo un patrón de barrido en sentido horario, sin utilizar memoria ni percepción global"
    
    def think(self) -> bool:
        if not self.is_connected():
            return False
        
        env = self.get_environment()
        if not env:
            return False
        
        if env.is_finished:
            return False
        
        # Debemos usar idle() para balancear los casos en que no limpiamos, así
        # podemos calcular la posición en el patrón a partir de las acciones consumidas
        is_cleaning_stage = env.actions_consumed % 2 == 0
        if is_cleaning_stage:
            if env.is_dirty:
                return self.suck()
            else:
                return self.idle()
        
        solution = self._solve_section(env.pos, env.cells_cleaned)
        return solution()
    
    # Resolución recursiva, resuelve en un patrón de barrido de sentido horario, a diferentes escalas
    # Utiliza la cantidad de acciones consumidas y la posición para saber en qué etapa se encuentra del patrón
    def _solve_section(self, rel_pos, section_cleaned_cells, section_size=128, desired_exit_dir=None):
        if desired_exit_dir is None:
            desired_exit_dir = self.idle
        
        if section_size == 1:
            return desired_exit_dir
        
        subsection_size = section_size // 2
        subsection_cell_total = (5 ** int(math.log2(subsection_size)))
        
        current_subsection = Section((2 * rel_pos.x) // section_size, (2 * rel_pos.y) // section_size)
        current_subsection_cleaned_cells = section_cleaned_cells % subsection_cell_total
        current_subsection_pos = current_subsection * subsection_size
        pos_rel_2_current_subsection = rel_pos - current_subsection_pos

        current_subsection_index = section_cleaned_cells // subsection_cell_total

        subsection_exit_dir = None
        if 0 <= current_subsection_index <= 2:
            subsection_exit_dir = self._get_clockwise_move_dir(current_subsection)
        elif current_subsection_index == 3:
            if self._is_on_proper_side(desired_exit_dir, current_subsection):
                subsection_exit_dir = self.idle
            else:
                subsection_exit_dir = desired_exit_dir
        elif current_subsection_index == 4:
            subsection_exit_dir = desired_exit_dir

        return self._solve_section(pos_rel_2_current_subsection, current_subsection_cleaned_cells, subsection_size, subsection_exit_dir)
    
    # Devuelve si estamos en el lugar correcto de una sección
    # tal que podamos salir por el lado deseado
    def _is_on_proper_side(self, exit_dir, subsection: Section):
        if exit_dir == self.right and subsection.x == 1:
            return True
        if exit_dir == self.left and subsection.x == 0:
            return True
        if exit_dir == self.down and subsection.y == 1:
            return True
        if exit_dir == self.up and subsection.y == 0:
            return True
        return False

    # Devuelve en qué dirección movernos según la subsección en la que estamos
    # tal que sigamos un movimiento en sentido horario
    def _get_clockwise_move_dir(self, subsection):
        if subsection == Section(0, 0):
            return self.right
        if subsection == Section(1, 0):
            return self.down
        if subsection == Section(0, 1):
            return self.up
        if subsection == Section(1, 1):
            return self.left

    # Esto es solamente para simplificar la sintaxis de acceso a los datos del entorno
    # Se guardan en una clase tal que podamos acceder con notación de punto (e.g. env.pos.x o env.is_dirty)
    def get_environment(self) -> Perception:
        perception = self.get_perception()
        if not perception or perception.get('is_finished', True):
            return False
        
        env = Perception()
        pos = perception.get('position')
        env.pos = Position(pos[0], pos[1])
        env.is_dirty = perception.get('is_dirty')
        env.actions_consumed = 1000 - perception.get('actions_remaining')
        env.cells_cleaned = (env.actions_consumed + 1) // 2 - 1
        env.is_finished = perception.get('is_finished')

        return env
    
def run_example_agent_simulation(size_x: int = 8, size_y: int = 8, 
                                dirt_rate: float = 0.3, 
                                server_url: str = "http://localhost:5000",
                                verbose: bool = True) -> int:
    agent = ReflexAgent(server_url)
    
    try:
        if not agent.connect_to_environment(size_x, size_y, dirt_rate):
            return 0
        
        performance = agent.run_simulation(verbose)
        return performance
    
    finally:
        agent.disconnect()

if __name__ == "__main__":
    print("Reflex Agent")
    print("Make sure the environment server is running on localhost:5000")
    print()
    
    performance = run_example_agent_simulation(verbose=True)
    print(f"\nFinal performance: {performance}")
