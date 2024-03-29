%:- use_module('PyProbEC/ProbLogFiles/in_out.py').
% PROLOG-INDEPENDENT

holdsAt_(aux = true, 0).

holdsAt(F = V, T) :-
  T @> 0,
  allTimeStamps(Timestamps),
  previousTimeStamp(T, Timestamps, Tprev),
  holdsAt_(F = V, Tprev),
  \+ broken(F = V, Tprev, T).

holdsAt(F = V, T) :-
  T @> 0,
  allTimeStamps(Timestamps),
  previousTimeStamp(T, Timestamps, Tprev),
  initiatedAt(F = V, Tprev).

%holdsAt(F = V, T):-
%  \+ sdFluent(F),
%  T @> 0,
%  initiatedAt(F = V, Tprev),
%  Tprev < T,
%  \+ broken(F = V, Tprev, T). % crisp version contains a cut here

broken(F = V1, T1, T2):-
  allTimeStamps(Timestamps),
  previousTimeStamp(T2, Timestamps, T3),
  initiatedAt(F = V2, T3),
  V1 \= V2.

broken(F = V, T1, T2) :-
  allTimeStamps(Timestamps),
  previousTimeStamp(T2, Timestamps, T3),
  T3 > T1,
  broken(F = V, T1, T3).

previousTimeStampN(T, Timestamps, T, 0).
previousTimeStampN(T, Timestamps, TprevN, S) :-
    S > 0,
    previousTimeStamp(T, Timestamps, Tprev),
    S2 is S - 1,
    previousTimeStampN(Tprev, Timestamps, TprevN, S2).
