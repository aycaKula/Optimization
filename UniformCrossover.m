function [y1, y2] = UniformCrossover(x1, x2)
    % x1 and x2 are parent positions in search space; y1 and y2 are two offsprings
    
    alpha = randi([0,1],size(x1));
    
    y1 = alpha.*x1 + (1-alpha).*x2;
    y2 = alpha.*x2 + (1-alpha).*x1;

end