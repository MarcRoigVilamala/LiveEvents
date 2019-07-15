initiatedAt(interesting = true, T) :-
    happensAt(something, T),
    allTimeStamps(Timestamps),
    nextTimeStamp(T, Timestamps, Tnext),
    happensAt(something, Tnext).

initiatedAt(interesting = false, T) :-
    happensAt(nothing, T),
    allTimeStamps(Timestamps),
    previousTimeStamp(T, Timestamps, Tprev),
    happensAt(nothing, Tprev).


initiatedAt(abuse = true, T) :-
    initiatedAt(interesting = true, T),
    happensAt(atLeast(2, person), T),
    happensAt(overlapping(person, person), T).

initiatedAt(abuse = true, T) :-
    initiatedAt(interesting = true, T),
    happensAt(atLeast(1, person), T),
    isAnimal(A),
    happensAt(atLeast(1, A), T),
    happensAt(overlapping(person, A), T).

initiatedAt(abuse = false, T) :-
    initiatedAt(interesting = false, T).


initiatedAt(run_over = true, T) :-
    initiatedAt(interesting = true, T),
    happensAt(overlapping(truck, person), T).

initiatedAt(run_over = false, T) :-
    initiatedAt(interesting = false, T).

isAnimal(dog).

sdFluent( aux ).
