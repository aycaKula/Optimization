% https://www.youtube.com/watch?v=pW39nKyYlN4


% Problem definition
problem.CostFunction = @(x)MinOne(x);
problem.nVar = 10;

% Number of population
params.nPop = 20;
% max num of iterations
params.MaxIter = 100;

%Percantage of crossover
params.pC = 1; % how many offsprings will be created at each generation
params.mu = 0.1; % mutation rate 10 percent
params.beta = 1;

% Run GA

out = RunGA(problem, params);