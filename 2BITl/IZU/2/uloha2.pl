list_lenght([],0).
list_lenght([_|TAIL],N) :- list_lenght(TAIL,N1), N is N1+1.

list_split(L,0,[],L).
list_split([X|Xs],N,[X|Ys],Zs):- N > 0, N1 is N - 1, list_split(Xs,N1,Ys,Zs).