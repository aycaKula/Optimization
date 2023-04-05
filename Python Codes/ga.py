from ypstruct import structure
import numpy as np

def run(problem, params):

    # Extract information
    cost_func = problem.cost_func
    num_var = problem.num_var
    var_min = problem.var_min
    var_max = problem.var_max

    # GA parameters
    max_iter = params.max_iter
    n_pop = params.n_pop
    beta = params.beta
    pc = params.pc #proportion of children / main population
    num_offspring = int(np.round(pc*n_pop/2)*2)
    gamma = params.gamma
    mu = params.mu
    sigma = params.sigma

    # Create initial population
    empty_individual = structure()
    empty_individual.position = None
    empty_individual.cost = None

    # Initialize population
    # for each population member create empty individuals
    population_members = empty_individual.repeat(n_pop)

    # best solution ever found
    bestsol = empty_individual.deepcopy()
    bestsol.cost = np.inf

    # for each popultion member we have to define:
    for i in range(n_pop):
        population_members[i].position = np.random.uniform(var_min, var_max, num_var)
        population_members[i].cost = cost_func(population_members[i].position)

        if population_members[i].cost < bestsol.cost:
            bestsol = population_members[i].deepcopy()

    # best cost of iterations
    bestcost = np.empty(max_iter)

    # Main Loop
    for it in range(max_iter):

        costs = np.array([x.cost for x in population_members])
        avg_cost = np.mean(costs)
        if avg_cost != 0:
            costs = costs/avg_cost
        probs = np.exp(-beta*costs) # selection probabilities are selected


        offsprings = [] # means number of children
        for _ in range(num_offspring//2): # how many offsprings we are going to have
            # # select parents
            # q = np.random.permutation(n_pop)
            # p1 = population_members[q[0]]
            # p2 = population_members[q[1]]

            # perform roulette wheel selection
            p1 = population_members[roulette_wheel_selection(probs)]
            p2 = population_members[roulette_wheel_selection(probs)]

            # perform crossover
            c1, c2 = crossover(p1,p2,gamma)

            # perform mutation
            c1 = mutate(c1, mu, sigma)
            c2 = mutate(c2, mu, sigma)

            # Apply bounds
            apply_bound(c1, var_min, var_max)
            apply_bound(c2, var_min, var_max)

            # Evaluate first offspring
            c1.cost = cost_func(c1.position)
            if c1.cost < bestsol.cost:
                bestsol = c1.deepcopy()

            # Evaluate second offspring
            c2.cost = cost_func(c2.position)
            if c2.cost < bestsol.cost:
                bestsol = c2.deepcopy()

            # Add offsprings to population
            offsprings.append(c1)
            offsprings.append(c2)

        # Merge, sort and select
        population_members += offsprings
        sorted(population_members, key = lambda x: x.cost)
        population_members = population_members[0:n_pop]

        # store best cost
        bestcost[it] = bestsol.cost

        # show iteration information
        print("Iteration {}: Best Cost = {}".format(it, bestcost[it]))

    out = structure()
    out.pop = population_members
    out.bestsol = bestsol
    out.bestcost = bestcost
    return out


def crossover(p1,p2, gamma = 0.1):
    c1 = p1.deepcopy() # structure is a reference type therefore we must use deepcopy
    c2 = p2.deepcopy()
    alpha = np.random.uniform(-gamma,1+gamma, *c1.position.shape) # astrict for converts tuple to distinct list elements
    # new offspring
    c1.position = alpha * p1.position + (1-alpha) * p2.position
    c2.position = alpha * p2.position + (1 - alpha) * p1.position
    return c1, c2

def mutate(x, mu, sigma):
    # sigma: mutation step size
    # mu: mutation rate
    y = x.deepcopy()
    flag = np.random.rand(*x.position.shape) <= mu # indicates where to apply mutation
    ind = np.argwhere(flag)
    y.position[ind] += sigma*np.random.randn(*ind.shape)
    return y

def apply_bound(x, var_min, var_max):
    x.position = np.maximum(x.position, var_min)
    x.position = np.minimum(x.position, var_max)

def roulette_wheel_selection(p):
    c = np.cumsum(p)
    r = sum(p)*np.random.rand()
    ind = np.argwhere(r <= c)
    return ind[0][0]