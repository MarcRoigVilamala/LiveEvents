initiatedAt(videoOnly = true, T) :-
    happensAt(something, T),
    allTimeStamps(Timestamps),
    nextTimeStamp(T, Timestamps, Tnext),
    happensAt(something, Tnext).

initiatedAt(videoOnly = false, T) :-
    happensAt(nothing, T),
    allTimeStamps(Timestamps),
    previousTimeStamp(T, Timestamps, Tprev),
    happensAt(nothing, Tprev).


initiatedAt(videoAndObjDet = true, T) :-
    initiatedAt(videoOnly = true, T),
    happensAt(atLeast(2, person), T),
    happensAt(overlapping(person, person), T).

initiatedAt(videoAndObjDet = true, T) :-
    initiatedAt(videoOnly = true, T),
    happensAt(atLeast(1, person), T),
    isAnimal(A),
    happensAt(atLeast(1, A), T),
    happensAt(overlapping(person, A), T).

initiatedAt(videoAndObjDet = false, T) :-
    initiatedAt(videoOnly = false, T).


initiatedAt(run_over = true, T) :-
    initiatedAt(videoOnly = true, T),
    happensAt(overlapping(truck, person), T).

initiatedAt(run_over = false, T) :-
    initiatedAt(videoOnly = false, T).

isAnimal(dog).

sdFluent( aux ).
