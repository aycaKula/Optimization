clc;
clear;
close all;

%% Problem definition

CostFunction = @(x) Sphere(x); % Cost function

nVar = 5; % Number of unknown (decision) variables % 5 dimensional space

VarSize = [1 nVar]; % Matrix size of Decision Variables

VarMin = -10; % Lower bound of decision variables
VarMax = 10;  % Upper bound of decision variables

%% Parameters of PSO

MaxIt = 1000;  % Maximum number of iterations

nPop = 50;    % Population size (swarm size)

w = 1;        % Inertia Coefficient
wdamp = 0.99; % damping ratio of inertia coef
c1 = 2;       % Personal acceleration coefficient
c2 = 2;       % Social acceleration coefficient

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
        
        % update position
        particle(i).Position = particle(i).Position + particle(i).Velocity;
         
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

figure;
semilogy(BestCosts, 'Linewidth', 1.2);
xlabel('Iteration')
ylabel('Best Cost')