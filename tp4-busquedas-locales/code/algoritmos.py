import time, random, math

class BaseAlgorithm:

    def __init__(self, name):
        self._name = name
        self._initialize()
    
    def _initialize(self, env_n=0, size=8, max_states=10000):
        self._env_n = env_n
        self._size = size
        self._max_states = max_states
        self._best_solution = None
        self._best_h = float('inf')
        self._best_h_per_iter = []
        self._explored_states = 0
        self._success = False
        self._should_stop = False
        self._time = None
        self._rng = random.Random(env_n)

    def run(self, env_n=0, size=8, max_states=10000, debug=False):
        self._initialize(env_n, size, max_states)

        start_time = time.time()
        
        results = self._start()
        self._update_stats(results)
        if (debug): self._print_solution(self._best_solution)

        while (self._explored_states < self._max_states and not self._success and not self._should_stop):
            results = self._step()
            self._update_stats(results)
            if (debug): self._print_solution(self._best_solution)

        end_time = time.time()
        self._time = end_time - start_time

        return {
            'algorithm_name': self._name,
            'env_n': self._env_n,
            'size': self._size,
            'best_solution': self._best_solution,
            'H': self._best_h,
            'states': self._explored_states,
            'time': self._time,
            'success': self._success,
            'best_h_per_iter': self._best_h_per_iter
        }
    
    def _start(self):
        pass
    
    def _step(self):
        raise NotImplementedError()
    
    def _update_stats(self, results):
        best_solution_current_step = results.get('solution', results.get('best_solution'))
        best_h_current_step = results.get('h', results.get('best_h', self._h_func(best_solution_current_step)))
        
        self._best_solution = best_solution_current_step if best_h_current_step < self._best_h else self._best_solution
        self._best_h = min(best_h_current_step, self._best_h)
        self._best_h_per_iter.append(self._best_h)
        self._explored_states += results.get('explored_states')
        self._success = self._best_h == 0
        self._should_stop = results.get('should_stop', False)
    
    def _h_func(self, solution):
        # Buscamos reinas en la misma diagonal (nunca están en la misma fila)
        threatened = 0
        for col1 in range(self._size):
            for col2 in range(col1 + 1, self._size):
                row1 = solution[col1]
                row2 = solution[col2]
                if abs(row2 - row1) == abs(col2 - col1):
                    threatened += 1
        
        return threatened
    
    def _get_neighboring_solutions(self, solution):
        neighbors = []
        n = len(solution)

        for i in range(n):
            for j in range(i + 1, n):
                neighbor = solution.copy()
                neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
                neighbors.append(neighbor)

        return neighbors

    def _generate_random_neighboring_solution(self, solution):
        n = len(solution)
        i, j = self._rng.sample(range(n), 2)
        neighbor = solution.copy()
        neighbor[i], neighbor[j] = neighbor[j], neighbor[i]
        return neighbor
    
    def _generate_random_solution(self, size=None):
        if size is None:
            size = self._size
        
        board = list(range(size))
        self._rng.shuffle(board)
        return board
    
    def _print_solution(self, solution):
        for row in range(self._size):
            line = ''
            for col in range(self._size):
                if solution[col] == row:
                    line += 'Q '
                else:
                    line += '. '
            print(line)
        print()


class RandomAlgorithm(BaseAlgorithm):
    def __init__(self, name='random'):
        super().__init__(name)

    def _step(self):
        return {
            'solution': self._generate_random_solution(),
            'explored_states': 1
        }


class HillClimbing(BaseAlgorithm):
    def __init__(self, name='hill_climbing'):
        super().__init__(name)
        self._current_solution = None

    def _start(self):
        initial_solution = self._generate_random_solution()
        self._current_solution = initial_solution

        return {
            'solution': initial_solution,
            'explored_states': 1
        }
    
    def _step(self):
        neighboring_solutions = self._get_neighboring_solutions(self._current_solution)
        better_solutions, best_h = self._choose_best_solutions(neighboring_solutions, max_h=self._best_h-1)

        solution = self._current_solution
        if len(better_solutions) > 0:
            solution = self._rng.choice(better_solutions)

        return {
            'solution': solution,
            'h': best_h,
            'explored_states': len(neighboring_solutions),
            'should_stop': len(better_solutions) == 0
        }
    
    def _choose_best_solutions(self, solutions, max_h=float('inf')):
        best_solutions = []
        best_h = max_h
        for solution in solutions:
            h = self._h_func(solution)
            if h < best_h:
                best_h = h
                best_solutions = [solution]
            elif h == best_h:
                best_solutions.append(solution)
        
        return best_solutions, best_h


class SimulatedAnnealing(BaseAlgorithm):
    def __init__(self, name='simulated_annealing', initial_temp=1000, cooling_rate=0.99, stop_temp=1e-3):
        super().__init__(name)
        self._current_solution = None
        self._current_h = None
        self._temp = initial_temp
        self._cooling_rate = cooling_rate
        self._stop_temp = stop_temp

    def _start(self):
        self._current_solution = self._generate_random_solution()
        self._current_h = self._h_func(self._current_solution)
        return {
            'solution': self._current_solution,
            'h': self._current_h,
            'explored_states': 1
        }

    def _step(self):
        neighbor = self._generate_random_neighboring_solution(self._current_solution)
        neighbor_h = self._h_func(neighbor)

        delta = neighbor_h - self._current_h
        accept = False

        if delta <= 0:
            accept = True
        else:
            probability = math.e ** (-delta / self._temp)
            accept = self._rng.random() < probability

        if accept:
            self._current_solution = neighbor
            self._current_h = neighbor_h

        self._temp *= self._cooling_rate
        should_stop = self._temp < self._stop_temp

        return {
            'solution': self._current_solution,
            'h': self._current_h,
            'explored_states': 1,
            'should_stop': should_stop
        }