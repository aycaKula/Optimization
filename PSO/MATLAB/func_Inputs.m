
%% Problem definition
problem.CostFunction = @(x) Sphere(x); % Cost function

problem.nVar = 10; % Number of unknown (decision) variables % 5 dimensional space

problem.VarMin = -10; % Lower bound of decision variables
problem.VarMax = 10;  % Upper bound of decision variables

%% Parameters of PSO

% constriction coef
kappa = 1;
phi1 = 2.05;
phi2 = 2.05;
phi = phi1 + phi2;
chi = 2*kappa/abs(2-phi-sqrt(phi^2-4*phi));

params.MaxIt = 1000;  % Maximum number of iterations

params.nPop = 50;    % Population size (swarm size)

params.w = chi;        % Inertia Coefficient
params.wdamp = 1; % damping ratio of inertia coef
params.c1 = chi*phi1;       % Personal acceleration coefficient
params.c2 = chi*phi2;       % Social acceleration coefficient

%% call Function

out = PSOfunc(problem, params);
