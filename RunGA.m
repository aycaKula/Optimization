function out = RunGA(problem,params)
    % problem
    CostFunction = problem.CostFunction;
    nVar = problem.nVar;
    
    % Params
    nPop = params.nPop;
    MaxIter = params.MaxIter;
    pC = params.pC; 
    mu = params.mu;
    % nC offsprings
    nC = round(pC*nPop/2)*2; % num of offsprings should be an even number
    beta = params.beta;
    
    % Template for empty individuals
    empty_individual.Position = [];
    empty_individual.Cost = [];
    
    % Best Solution ever Found
    bestsol.Cost = inf; % initiliaze with worst solution and try to reach the best
    
    % Initialization
    pop = repmat(empty_individual, nPop, 1);%repeat empty indiviaduals
    
    for i = 1:nPop
        % Generate random solution
        pop(i).Position = randi([0,1], 1, nVar); %generate random solutions
        
        % Evaluate random solution
        pop(i).Cost = CostFunction(pop(i).Position);
        
        % Compare solution to best solution ever found
        if pop(i).Cost <  bestsol.Cost
            bestsol = pop(i);
        end
    end
    
    % best cost of iterations
    bestcost = nan(MaxIter,1);
    
    %Main Loop
    for It = 1:MaxIter
        %Selection propabilities
        c = [pop.Cost];
        avgc = mean(c);
        if avgc~=0
            c = c/avgc;
        end
        probs = exp(-beta*c);
        
        % Initialize Offsprings Population
        popC = repmat(empty_individual, nC/2,2);
        
        % Crossover
        for k = 1:nC/2
            %               %%%%%%%%%%%%%% deleted after RouletteWheelSelection
            %             % Select parents randomly
            %             q = randperm(nPop);
            %             p1 = pop(q(1)); % first parent
            %             p2 = pop(q(1)); % second parent
            %
            p1 = pop(RouletteWheelSelection(probs)); % first parent
            p2 = pop(RouletteWheelSelection(probs)); % second parent
            
            
            %             % perform crossover
            %             [popC(k,1).Position, popC(k,2).Position] = ...
            %                 SinglePointCrossover(p1.Position, p2.Position);
            
            % perform crossover
            [popC(k,1).Position, popC(k,2).Position] = ...
                DoublePointCrossover(p1.Position, p2.Position);
            
        end
        
        
        % Convert popC to single-column matrix
        popC = popC(:);
        
        % Mutation
        for l = 1:nC
            % Perform mutation
            pop(l).Position = Mutate(popC(1).Position, mu);
            
            % Evaluation
            pop(l).Cost = CostFunction(popC(1).Position);
            
            % Compare solution to best solution ever found
            if pop(l).Cost <  bestsol.Cost
                bestsol = pop(l);
            end
        end
        
        % Update best cost of iteration
        bestcost(It) = bestsol.Cost;
        
        % Merge populations
        pop = [pop;popC];
        
        % Sort population
        [~, so] = sort([pop.Cost]);
        pop = pop(so);
        
        % Remove extra individuals
        pop = pop(1:nPop);
        
        % display isteration info
        disp(['itertion' num2str(It) ': best cost = ' num2str(bestcost(It))]);
        
    end
    
    out.pop = pop;
    out.bestsol = bestsol;
    out.bestcost = bestcost;
end

