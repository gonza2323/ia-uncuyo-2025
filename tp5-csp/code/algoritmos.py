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
        self._explored_states = 0
        self._success = False
        self._should_stop = False
        self._time = None
        self._rng = random.Random(env_n)

    def run(self, env_n=0, size=8, max_states=10000, debug=False):
        self._initialize(env_n, size, max_states)

        start_time = time.time()
        
        results = self._start()

        if (results):
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
        }
    
    def _start(self):
        pass
    
    def _step(self):
        raise NotImplementedError()
    
    def _update_stats(self, results):
        best_solution_current_step = results.get('solution', results.get('best_solution', None))

        if best_solution_current_step:
            best_h_current_step = results.get('h', results.get('best_h', self._h_func(best_solution_current_step)))
            if best_h_current_step < self._best_h:
                self._best_solution = best_solution_current_step
                self._best_h = best_h_current_step

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

    def get_name(self):
        return self._name


class RandomAlgorithm(BaseAlgorithm):
    def __init__(self, name='Random'):
        super().__init__(name)

    def _start(self):
        return {
            'solution': self._generate_random_solution(),
            'explored_states': 1
        }

    def _step(self):
        return {
            'solution': self._generate_random_solution(),
            'explored_states': 1
        }


class HillClimbing(BaseAlgorithm):
    def __init__(self, name='HC'):
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
    def __init__(self, name='SA', initial_temp=1000, cooling_rate=0.99, stop_temp=1e-3):
        super().__init__(name)
        self._current_solution = None
        self._current_h = None
        self._initial_temp = initial_temp
        self._temp = initial_temp
        self._cooling_rate = cooling_rate
        self._stop_temp = stop_temp

    def _start(self):
        self._temp = self._initial_temp
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


class GeneticAlgorithm(BaseAlgorithm):
    def __init__(self, name='GA', population_size=50, mutation_rate=0.2):
        super().__init__(name)
        self._population_size = population_size
        self._mutation_rate = mutation_rate
        self._population = []

    def _start(self):
        self._population = [self._generate_random_solution() for _ in range(self._population_size)]
        best = min(self._population, key=self._h_func)
        return {
            'best_solution': best,
            'best_h': self._h_func(best),
            'explored_states': self._population_size
        }

    def _step(self):
        # Mantenemos al 10% mejor (elitismo)
        sorted_pop = sorted(self._population, key=self._h_func)
        elite_count = max(1, len(self._population) // 10)
        elite = sorted_pop[:elite_count]

        # Partially Mapped Crossover
        children = []
        while len(children) + len(elite) < self._population_size:
            # Elegimos los padres por torneo
            parent1 = self._tournament_selection(k=3)
            parent2 = self._tournament_selection(k=3)
            while parent2 == parent1:
                parent2 = self._tournament_selection(k=3)

            # Crossover
            child = self._pmx(parent1, parent2)
            children.append(child)

        self._population = elite + children

        # Mutaciones
        for i in range(len(self._population)):
            if self._rng.random() < self._mutation_rate:
                a, b = self._rng.sample(range(self._size), 2)
                self._population[i][a], self._population[i][b] = self._population[i][b], self._population[i][a]

        best = min(self._population, key=self._h_func)
        best_h = self._h_func(best)

        return {
            'best_solution': best,
            'best_h': best_h,
            'explored_states': self._population_size,
        }
    
    def _tournament_selection(self, k=3):
            candidates = self._rng.sample(self._population, k)
            return min(candidates, key=self._h_func)

    def _pmx(self, parent1, parent2):
        size = self._size
        cx1, cx2 = sorted(self._rng.sample(range(size + 1), 2))
        child = [None] * size

        # Genes padre 1
        child[cx1:cx2] = parent1[cx1:cx2]

        # Mapeo
        mapping = {parent1[i]: parent2[i] for i in range(cx1, cx2)}

        # Resto de los genes (padre 2)
        for i in range(size):
            if cx1 <= i < cx2:
                continue
            val = parent2[i]
            while val in mapping:
                val = mapping[val]
            child[i] = val

        return child


class CSPBacktracking(BaseAlgorithm):
    def __init__(self, name='CSP-BT'):
        super().__init__(name)
        self._assignment = None
        self._domains = None
        self._stack = None

    def _start(self):
        # Initialize empty assignment
        self._assignment = [None] * self._size
        # Shuffle domains for reproducibility
        self._domains = [self._rng.sample(range(self._size), self._size) for _ in range(self._size)]
        # Stack stores (column, remaining choices)
        self._stack = [(0, self._domains[0][:])]
        return {'explored_states': 1}

    def _step(self):
        if not self._stack:
            return {'should_stop': True, 'explored_states': 0}

        col, choices = self._stack.pop()
        while choices:
            row = choices.pop()
            if self._is_safe(col, row):
                self._assignment[col] = row
                if col + 1 == self._size:  # Full solution found
                    solution = self._assignment.copy()
                    self._assignment[col] = None
                    return {'solution': solution, 'explored_states': 1}
                else:
                    # Push current column with remaining choices for backtracking
                    self._stack.append((col, choices))
                    # Push next column with shuffled domain
                    self._stack.append((col + 1, self._domains[col + 1][:]))
                    return {'explored_states': 1}
        # No valid row, backtrack
        self._assignment[col] = None
        return {'explored_states': 1}

    def _is_safe(self, col, row):
        for c in range(col):
            r = self._assignment[c]
            if r == row or abs(r - row) == abs(c - col):
                return False
        return True


class CSPForwardChecking(BaseAlgorithm):
    def __init__(self, name='CSP-FC'):
        super().__init__(name)
        self._assignment = None
        self._domains = None
        self._solution_found = False
        self._explored_in_step = 0

    def _start(self):
        self._assignment = [None] * self._size
        # Shuffle domains per column for reproducibility
        self._domains = [self._rng.sample(range(self._size), self._size) for _ in range(self._size)]
        self._solution_found = False
        self._explored_in_step = 0

        return {'explored_states': 0}

    def _step(self):
        self._explored_in_step = 0
        solution = self._recursive_forward_check(0, [d[:] for d in self._domains])
        result = {'explored_states': self._explored_in_step}
        if solution is not None:
            result['solution'] = solution
        else:
            result['should_stop'] = True
        return result

    def _recursive_forward_check(self, col, domains):
        self._explored_in_step += 1

        if col == self._size:
            # full solution found
            return self._assignment.copy()

        for row in domains[col]:
            if self._is_safe(col, row):
                self._assignment[col] = row
                # prune domains for future columns
                new_domains = [d[:] for d in domains]
                valid = True
                for future_col in range(col + 1, self._size):
                    new_domains[future_col] = [r for r in new_domains[future_col] if r != row and abs(r - row) != abs(future_col - col)]
                    if not new_domains[future_col]:
                        valid = False
                        break

                if valid:
                    solution = self._recursive_forward_check(col + 1, new_domains)
                    if solution is not None:
                        return solution

                # backtrack
                self._assignment[col] = None

        return None

    def _is_safe(self, col, row):
        for c in range(col):
            r = self._assignment[c]
            if r == row or abs(r - row) == abs(c - col):
                return False
        return True