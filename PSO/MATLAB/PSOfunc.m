function out = PSOfunc(problem, params)

%% Problem definition

CostFunction = problem.CostFunction; % Cost function

nVar = problem.nVar; % Number of unknown (decision) variables % 5 dimensional space

VarSize = [1 nVar]; % Matrix size of Decision Variables

VarMin = problem.VarMin; % Lower bound of decision variables
VarMax = problem.VarMax;  % Upper bound of decision variables

%% Parameters of PSO

MaxIt = params.MaxIt;  % Maximum number of iterations

nPop = params.nPop;    % Population size (swarm size)

w = params.w;         % Inertia Coefficient
wdamp = params.wdamp; % damping ratio of inertia coef
c1 = params.c1;       % Personal acceleration coefficient
c2 = params.c2;       % Social acceleration coefficient

% 
MaxVelocity = (VarMax - VarMin)*0.2;
MinVelocity = -MaxVelocity;

%% Initialization

% particle templete
empty_particle.Position = [];
empty_particle.Velocity = [];
empty_particle.Cost = [];
empty_particle.Best.Position = [];
empty_particle.Best.Cost = [];

% create population array
particle = repmat(empty_particle, nPop ,1);

% Initialize the Global Best
GlobalBest.Cost = inf;

for i = 1:nPop
    
    % generate random solution
    particle(i).Position = unifrnd(VarMin, VarMax, VarSize); % random values
    
    % Initialize valocity
    particle(i).Velocity = zeros(VarSize);
    
    % Evaluation
    particle(i).Cost = CostFunction(particle(i).Position);
    
    % Update the Personal Best
    particle(i).Best.Position = particle(i).Position;
    particle(i).Best.Cost = particle(i).Cost;
    
    % update global best
    if particle(i).Best.Cost < GlobalBest.Cost
        GlobalBest = particle(i).Best ;
    end
    
end

% Array to hold best cost value on each iteration
BestCosts = zeros(MaxIt, 1);

%% Main Loop of PSO

for it = 1: MaxIt
    
    for i = 1:nPop
        
        % update velocity
        particle(i).Velocity = w*particle(i).Velocity ...
            + c1*rand(VarSize).*(particle(i).Best.Position - particle(i).Position)...
            + c2*rand(VarSize).*(GlobalBest.Position - particle(i).Position);
        
        % apply velocity limits
        particle(i).Velocity = max(particle(i).Velocity, MinVelocity);
        particle(i).Velocity = min(particle(i).Velocity, MaxVelocity);
        
        % update position
        particle(i).Position = particle(i).Position + particle(i).Velocity;
        
        % apply lower and upper bound limits
        particle(i).Position = max(particle(i).Position, VarMin);
        particle(i).Position = min(particle(i).Position, VarMax);
        
        % Evaluation
        particle(i).Cost = CostFunction(particle(i).Position);
        
        if particle(i).Cost < particle(i).Best.Cost
            
            particle(i).Best.Position = particle(i).Position;
            particle(i).Best.Cost = particle(i).Cost;
            
            if particle(i).Best.Cost < GlobalBest.Cost
                GlobalBest = particle(i).Best ;
            end
            
        end
        
    end
    
    % store best cost value
    BestCosts(it) = GlobalBest.Cost;
    
    % Display iteration information
    disp(['Iteration' num2str(it) ': Best Cost =' num2str(BestCosts(it))]);
    
    % Damping inertia coef
    w = w*wdamp;
    
end

%% Results
out.pop = particle;
out.BestSol = GlobalBest;
out.BestCosts = BestCosts;

figure;
semilogy(BestCosts, 'Linewidth', 1.2);
xlabel('Iteration')
ylabel('Best Cost')

end