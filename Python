from ypstruct import structure
import ga
import matplotlib.pyplot as plt

# Cost function
def sphere(x):
    return sum(x**2)

# Problem definition
# Problem is where you want to minimize the cost func
problem = structure()
problem.cost_func = sphere
problem.num_var = 5
problem.var_min = -10
problem.var_max = 10

# GA parameters
params = structure()
params.max_iter = 100
params.n_pop = 50
params.pc = 1
params.gamma = 0.1
params.mu = 0.01
params.sigma = 0.1
params.beta = 1

# GA parameters
out = ga.run(problem, params)

# results
# plt.plot(out.bestcost)
plt.semilogy(out.bestcost)
plt.xlim(0, params.max_iter)
plt.xlabel('Iterations')
plt.ylabel('Best cost')
plt.title('Genetic Algorithm')
plt.grid(True)
plt.show()


