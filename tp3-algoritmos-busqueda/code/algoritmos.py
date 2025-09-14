from random import choice
import time
from collections import deque
import heapq

class Vec2:
    def __init__(self, y: int = 0, x: int = 0):
        self.y: int = y
        self.x: int = x

    def __eq__(self, other) -> bool:
        if not isinstance(other, Vec2):
            return False
        return self.y == other.y and self.x == other.x
    
    def __hash__(self):
        return hash((self.y, self.x))
    
    def clamp_to_grid(self, grid):
        self.y = self.y if self.y >= 0 else 0
        self.y = self.y if self.y < grid.get_height() else grid.get_height()-1
        self.x = self.x if self.x >= 0 else 0
        self.x = self.x if self.x < grid.get_width() else grid.get_width()-1
        return self
    
    def manhattan_distance(self, other):
        return abs(self.y - other.y) + abs(self.x - other.x)
    
    def __add__(self, other): return Vec2(self.y + other.y, self.x + other.x)
    def __sub__(self, other): return Vec2(self.y - other.y, self.x - other.x)
    def __mul__(self, k): return Vec2(self.y * k, self.x * k)
    __rmul__ = __mul__

Pos = Vec2


class Grid:
    def __init__(self, grid: list[str]):
        self._grid = [list(row) for row in grid]
        self._height = len(self._grid)
        self._width = len(self._grid[0]) if self._height > 0 else 0

    def _normalize_index(self, key):
        if isinstance(key, Vec2):
            return key.y, key.x
        elif isinstance(key, tuple) and len(key) == 2:
            return key  # already (y, x)
        else:
            raise TypeError("Grid index must be a Vec2 or a (y, x) tuple")

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._grid[key]
        y, x = self._normalize_index(key)
        return self._grid[y][x]

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self._grid[key] = value
            return
        y, x = self._normalize_index(key)
        self._grid[y][x] = value

    def __repr__(self):
        return "\n".join("".join(row) for row in self._grid)
    
    def get_start_pos(self):
        for y, row in enumerate(self._grid):
            for x, val in enumerate(row):
                if val == 'S':
                    return Pos(y, x)
    
    def get_goal_pos(self):
        for y, row in enumerate(self._grid):
            for x, val in enumerate(row):
                if val == 'G':
                    return Pos(y, x)
    
    def get_height(self): return self._height
    def get_width(self): return self._width


class Algorithm:
    def __init__(self, name):
        self._name = name
        self._grid = None
        self._cost_fn = None
        self._max_actions = None
        self._start = None
        self._goal = None
        self._pos = None
        self._path = None
        self._actions = []
        self._visited = []
        self._explored_states = 0
        self._actions_count = 0
        self._actions_cost = 0
        self._success = False
        self._time = None

    def run(self, grid : Grid, cost_fn=lambda _ : 1, max_actions=float('inf')):
        self._initialize(grid, cost_fn, max_actions)
        
        start_time = time.time()
        self._calculate_solution()
        end_time = time.time()
        self._time = end_time - start_time
        
        return self._get_results()
    
    def _initialize(self, grid : Grid, cost_fn, max_actions):
        if self._grid != grid:
            self._grid = grid
            self._start = grid.get_start_pos()
            self._goal = grid.get_goal_pos()
        
        self._pos = self._start
        self._cost_fn = cost_fn
        self._max_actions = max_actions
        self._path = [self._start]
        self._actions = []
        self._visited = []
        self._explored_states = 0
        self._actions_count = 0
        self._actions_cost = 0
        self._success = False
        self._time = None
    
    def _get_results(self):
        return {
            'algorithm_name': self._name,
            'path': self._path if self._success else None,
            'actions': self._actions if self._success else None,
            'states_n': self._explored_states,
            'actions_count': self._actions_count if self._success else None,
            'actions_cost': self._actions_cost if self._success else None,
            'time': self._time,
            'solution_found': self._success,
        }

    def _is_valid_position(self, pos):
        return 0 <= pos.x < self._grid.get_width() and 0 <= pos.y < self._grid.get_height()
    
    def _reconstruct_path(self, came_from, current):
        path = []
        actions = []
        
        while current in came_from:
            path.append(current)
            parent, action = came_from[current]
            actions.append(action)
            current = parent
        
        path.append(self._start)
        path.reverse()
        actions.reverse()
        
        return path, actions


ACTIONS = [
    Vec2( 0, 1), # derecha
    Vec2(-1, 0), # arriba
    Vec2( 0,-1), # izquierda
    Vec2( 1, 0), # abajo
]


class RandomSearch(Algorithm):
    def __init__(self, name='Random'):
        super().__init__(name)
    
    def _calculate_solution(self):
        while True:
            if self._pos not in self._visited:
                self._visited.append(self._pos)
                self._explored_states += 1
            
            tile = self._grid[self._pos]

            if tile == 'G':
                self._success = True
                return

            if tile == 'H':
                return

            if self._actions_count >= self._max_actions:
                return
            
            action = choice(ACTIONS)
            self._actions.append(action)
            self._actions_count += 1
            self._actions_cost += self._cost_fn(action)
            
            new_pos = (self._pos + action).clamp_to_grid(self._grid)
            self._path.append(new_pos)
            self._pos = new_pos


class BFS(Algorithm):
    def __init__(self, name='BFS'):
        super().__init__(name)
    
    def _calculate_solution(self):
        queue = deque([self._start])
        visited = set([self._start])
        came_from = {}
        
        while queue:
            current = queue.popleft()
            self._explored_states += 1
            
            if current == self._goal:
                self._path, self._actions = self._reconstruct_path(came_from, current)
                
                if len(self._actions) <= self._max_actions:
                    self._success = True
                    self._actions_count = len(self._actions)
                    self._actions_cost = sum(self._cost_fn(action) for action in self._actions)
                
                return
            
            for action in ACTIONS:
                neighbor = current + action
                
                if (self._is_valid_position(neighbor) and 
                    neighbor not in visited and 
                    self._grid[neighbor] != 'H'):
                    
                    visited.add(neighbor)
                    came_from[neighbor] = (current, action)
                    queue.append(neighbor)


class DFS(Algorithm):
    def __init__(self, name='DFS', depth_limit=None):
        super().__init__(name)
        self._depth_limit = depth_limit
        if depth_limit is not None:
            self._name = f'DLS-{depth_limit}'
    
    def _calculate_solution(self):
        visited = set()
        came_from = {}
        
        stack = [(self._start, 0, 0)]
        
        while stack:
            current, depth, path_length = stack.pop()
            
            if current in visited:
                continue
            
            if self._depth_limit is not None and depth > self._depth_limit:
                continue
            
            if path_length > self._max_actions:
                continue
            
            visited.add(current)
            self._explored_states += 1
            
            if current == self._goal:
                self._path, self._actions = self._reconstruct_path(came_from, self._goal)
                self._success = True
                self._actions_count = len(self._actions)
                self._actions_cost = sum(self._cost_fn(action) for action in self._actions)
                return
            
            if self._grid[current] == 'H':
                continue
            
            for action in reversed(ACTIONS):
                neighbor = current + action
                
                if (self._is_valid_position(neighbor) and 
                    neighbor not in visited and 
                    self._grid[neighbor] != 'H'):
                    
                    came_from[neighbor] = (current, action)
                    stack.append((neighbor, depth + 1, path_length + 1))


class UCS(Algorithm):
    def __init__(self, name='UCS'):
        super().__init__(name)
    
    def _calculate_solution(self):
        counter = 0
        heap = [(0, counter, self._start)]
        visited = set()
        came_from = {}
        cost_so_far = {self._start: 0}
        counter += 1
        
        while heap:
            current_cost, _, current = heapq.heappop(heap)
            
            if current in visited:
                continue
            
            visited.add(current)
            self._explored_states += 1
            
            if current == self._goal:
                self._path, self._actions = self._reconstruct_path(came_from, current)
                
                if len(self._actions) <= self._max_actions:
                    self._success = True
                    self._actions_count = len(self._actions)
                    self._actions_cost = current_cost
                
                return
            
            if self._grid[current] == 'H':
                continue
            
            for action in ACTIONS:
                neighbor = current + action
                
                if (self._is_valid_position(neighbor) and 
                    self._grid[neighbor] != 'H'):
                    
                    new_cost = current_cost + self._cost_fn(action)
                    
                    if (neighbor not in cost_so_far or 
                        new_cost < cost_so_far[neighbor]):
                        
                        cost_so_far[neighbor] = new_cost
                        came_from[neighbor] = (current, action)
                        heapq.heappush(heap, (new_cost, counter, neighbor))
                        counter += 1


class AStar(Algorithm):
    def __init__(self, name='A*', heuristic_selector=None):
        super().__init__(name)
        if heuristic_selector is None:
            self._heuristic_selector = lambda cost_fn: lambda pos1, pos2: pos1.manhattan_distance(pos2)
        else:
            self._heuristic_selector = heuristic_selector
    
    def _calculate_solution(self):
        heuristic_fn = self._heuristic_selector(self._cost_fn)
        
        counter = 0
        heap = [(0, counter, self._start)]
        visited = set()
        came_from = {}
        g_score = {self._start: 0}
        counter += 1
        
        while heap:
            current_f, _, current = heapq.heappop(heap)
            
            if current in visited:
                continue
            
            visited.add(current)
            self._explored_states += 1
            
            if current == self._goal:
                self._path, self._actions = self._reconstruct_path(came_from, current)
                
                if len(self._actions) <= self._max_actions:
                    self._success = True
                    self._actions_count = len(self._actions)
                    self._actions_cost = g_score[current]
                
                return
            
            if self._grid[current] == 'H':
                continue
            
            for action in ACTIONS:
                neighbor = current + action
                
                if (self._is_valid_position(neighbor) and 
                    self._grid[neighbor] != 'H'):
                    
                    tentative_g = g_score[current] + self._cost_fn(action)
                    
                    if (neighbor not in g_score or 
                        tentative_g < g_score[neighbor]):
                        
                        g_score[neighbor] = tentative_g
                        h_score = heuristic_fn(neighbor, self._goal)
                        f_score = tentative_g + h_score
                        
                        came_from[neighbor] = (current, action)
                        heapq.heappush(heap, (f_score, counter, neighbor))
                        counter += 1
