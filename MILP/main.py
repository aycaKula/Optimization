from mip import *

# CREATING MODEL
m = Model() # MILP problem with default settings
# m = Model(sense=MAXIMIZE, solver_name=CBC) # use GRB for Gurobi


# DECISION VARIABLES
x = m.add_var() # Decision variables are added

n = 10 # for n binary decision variables
y = [ m.add_var(var_type=BINARY) for i in range(n) ]

# Define bounds
z = m.add_var(name='zCost', var_type=INTEGER, lb=-10, ub=10)

# If you do not store these references, you can get them afterwards using the Model function
vz = m.var_by_name('zCost')
vz.ub = 5

# CONSTRAINTS
# The constraint 𝑥 + 𝑦 ≤ 10 can be easily included within model m
m += x + y <= 10

m += xsum(w[i]*x[i] for i in range(n)) <= c

m += xsum(w[i]*x[i] for i in range(n) if i%2 == 0) <= c

# name constraints.
m += xsum(w[i]*x[i] for i in range(n) if i%2 == 0) <= c, 'even_sum'

# As with variables, reference of constraints can be retrieved by their names
constraint = m.constr_by_name('even_sum')


# OBJECTIVE FUNCTION

m.objective = xsum(c[i]*x[i] for i in range(n)) # default is minimize
# m.objective = minimize(xsum(c[i]*x[i] for i in range(n)))

# Saving, Loading and Checking Model Properties
m.write('model.lp')
m.read('model.lp')
print('model has {} vars, {} constraints and {} nzs'.format(m.num_cols, m.num_rows, m.num_nz))