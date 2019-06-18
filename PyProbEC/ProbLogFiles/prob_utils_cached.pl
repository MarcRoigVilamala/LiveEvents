:- use_module('PyProbEC/ProbLogFiles/in_out.py').
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% ER utils
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%
% Gives all timepoints
%
%allTimePoints(SL):- findall(T, (holdsAt(F = V, T), number(T)), L), sort_no_duplicates(L, SL).
%allTimePoints([0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]).
%
% Gives all ID instances
%
%allIDs(IDs):- findall(ID, holdsAt(appearance(ID)=_,_),IDs1), sort(IDs1, IDs).
%allIDs([id0, id1, id2]).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Cartesian product
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

cartesian([], _L, []).
cartesian([A|N], L, M) :-
             pair(A,L,M1),
             cartesian(N, L, M2),
             append(M1, M2, M).
pair(_A, [], []).
pair(A, [B|L], [[A,B]|N] ) :- pair(A, L, N).

% cartesian product, without pairs of the same element
cartesianUnique([], _L, []).
cartesianUnique([A|N], L, M) :-
             pair2(A,L,M1),
             cartesianUnique(N, L, M2),
             append(M1, M2, M).
pair2(_A, [], []).
pair2(A, [B|L], [[A,B]|N] ) :- pair2(A, L, N), A\=B.
pair2(A, [A|L], N ):- pair2(A, L, N).


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Membership
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

member(T, [T | _]).
member(T, [_ | Ts]) :- member(T, Ts).
