% PROLOG-INDEPENDENT

holdsAt_(aux = true, 0).

holdsAt(F = V, T) :-
  \+ sdFluent(F),
  T @> 0,
  allTimePoints(Timepoints),
  previousTimePoint(T, Timepoints, Tprev),
  holdsAt_(F = V, Tprev),
  \+ broken(F = V, Tprev, T).

holdsAt(F = V, T) :-
  \+ sdFluent(F),
  T @> 0,
  allTimePoints(Timepoints),
  previousTimePoint(T, Timepoints, Tprev),
  initiatedAt(F = V, Tprev).

%holdsAt(F = V, T):-
%  \+ sdFluent(F),
%  T @> 0,
%  initiatedAt(F = V, Tprev),
%  Tprev < T,
%  \+ broken(F = V, Tprev, T). % crisp version contains a cut here

broken(F = V1, T1, T2):-
  allTimePoints(Timepoints),
  previousTimePoint(T2, Timepoints, T3),
  initiatedAt(F = V2, T3),
  V1 \= V2.

broken(F = V, T1, T2) :-
  allTimePoints(Timepoints),
  previousTimePoint(T2, Timepoints, T3),
  T3 > T1,
  broken(F = V, T1, T3).

%previousTimePoint(T, Tprev):- Tprev is T - 40.
%previousTimePoint(T, Tprev):- Tprev is T - 8.
