function y = Mutate(x, mu)
    flag = rand(size(x)) < mu;
    
    % logical indexing
    y = x;   
    y(flag) = 1 - x(flag); 
    
end