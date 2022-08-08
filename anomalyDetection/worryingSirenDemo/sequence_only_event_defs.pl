atTime(X, X).

wrapper(X, Y) :- sound(X, Y).

wraps(safeEnv, childrenPlaying).
wraps(safeEnv, streetMusic).

wraps(worryingSound, gunShot).
wraps(worryingSound, siren).

sound(-1, u_). % Ignore this, it is just to define the format for the sound clause

% Number of timestamps to look at (should be min the length of the sequence)
givenRemaining(5).

holdsAt(ceAirConditioner = true, T) :-
    givenRemaining(Remaining),
    sequence([airConditioner, airConditioner], Remaining, T).

holdsAt(ceCarHorn = true, T) :-
    givenRemaining(Remaining),
    sequence([carHorn, carHorn], Remaining, T).

holdsAt(ceChildrenPlaying = true, T) :-
    givenRemaining(Remaining),
    sequence([childrenPlaying, childrenPlaying], Remaining, T).

holdsAt(ceDogBark = true, T) :-
    givenRemaining(Remaining),
    sequence([dogBark, dogBark], Remaining, T).

holdsAt(ceDrilling = true, T) :-
    givenRemaining(Remaining),
    sequence([drilling, drilling], Remaining, T).

holdsAt(ceEngineIdling = true, T) :-
    givenRemaining(Remaining),
    sequence([engineIdling, engineIdling], Remaining, T).

holdsAt(ceGunShot = true, T) :-
    givenRemaining(Remaining),
    sequence([gunShot, gunShot], Remaining, T).

holdsAt(ceJackhammer = true, T) :-
    givenRemaining(Remaining),
    sequence([jackhammer, jackhammer], Remaining, T).

holdsAt(ceSiren = true, T) :-
    givenRemaining(Remaining),
    sequence([siren, siren], Remaining, T).

holdsAt(ceStreetMusic = true, T) :-
    givenRemaining(Remaining),
    sequence([streetMusic, streetMusic], Remaining, T).

holdsAt(ceWorryingSiren = true, T) :-
    givenRemaining(Remaining),
    sequence([safeEnv, siren, exclude(safeEnv), siren, exclude(safeEnv), siren, exclude(safeEnv)], Remaining, T).

holdsAt(ceWorryingSiren = true, T) :-
    givenRemaining(Remaining),
    allTimeStamps(Timestamps),
    previousTimeStamp(T, Timestamps, Tprev),
    holdsAt_(ceWorryingSiren = true, Tprev),
    sequence([exclude(safeEnv)], Remaining, T),
    sequence([worryingSound, worryingSound], Remaining, T).
