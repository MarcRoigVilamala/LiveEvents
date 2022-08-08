atTime(X, X).

wrapper(X, Y) :- sound(X, Y).

wraps(safeEnv, childrenPlaying).
wraps(safeEnv, streetMusic).

wraps(worryingSound, gunShot).
wraps(worryingSound, siren).

sound(-1, u_). % Ignore this, it is just to define the format for the sound clause

isNegation(notAirConditioner, airConditioner).
isNegation(notCarHorn, carHorn).
isNegation(notChildrenPlaying, childrenPlaying).
isNegation(notDogBark, dogBark).
isNegation(notDrilling, drilling).
isNegation(notEngineIdling, engineIdling).
isNegation(notGunShot, gunShot).
isNegation(notJackhammer, jackhammer).
isNegation(notSiren, siren).
isNegation(notStreetMusic, streetMusic).

isNegation(notSafeEnv, safeEnv).
isNegation(notWorryingSound, worryingSound).

% Number of timestamps to look at (should be min the length of the sequence)
givenRemaining(5).

initiatedAt(ceAirConditioner = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([airConditioner, airConditioner], Remaining, T).

initiatedAt(ceAirConditioner = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notAirConditioner], Remaining, T).

initiatedAt(ceCarHorn = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([carHorn, carHorn], Remaining, T).

initiatedAt(ceCarHorn = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notCarHorn], Remaining, T).

initiatedAt(ceChildrenPlaying = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([childrenPlaying, childrenPlaying], Remaining, T).

initiatedAt(ceChildrenPlaying = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notChildrenPlaying], Remaining, T).

initiatedAt(ceDogBark = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([dogBark, dogBark], Remaining, T).

initiatedAt(ceDogBark = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notDogBark], Remaining, T).

initiatedAt(ceDrilling = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([drilling, drilling], Remaining, T).

initiatedAt(ceDrilling = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notDrilling], Remaining, T).

initiatedAt(ceEngineIdling = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([engineIdling, engineIdling], Remaining, T).

initiatedAt(ceEngineIdling = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notEngineIdling], Remaining, T).

initiatedAt(ceGunShot = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([gunShot, gunShot], Remaining, T).

initiatedAt(ceGunShot = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notGunShot], Remaining, T).

initiatedAt(ceJackhammer = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([jackhammer, jackhammer], Remaining, T).

initiatedAt(ceJackhammer = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notJackhammer], Remaining, T).

initiatedAt(ceSiren = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([siren, siren], Remaining, T).

initiatedAt(ceSiren = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notSiren], Remaining, T).

initiatedAt(ceStreetMusic = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([streetMusic, streetMusic], Remaining, T).

initiatedAt(ceStreetMusic = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notStreetMusic], Remaining, T).

initiatedAt(ceWorryingSiren = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notSafeEnv, siren, notSafeEnv, siren, notSafeEnv, siren, safeEnv], Remaining, T).

initiatedAt(ceWorryingSiren = true, T) :-
    givenRemaining(Remaining),
    allTimeStamps(Timestamps),
    previousTimeStamp(T, Timestamps, Tprev),
    holdsAt_(ceWorryingSiren = true, Tprev),
    sequenceEndingAt([notSafeEnv], Remaining, T),
    sequenceEndingAt([worryingSound, worryingSound], Remaining, T).

initiatedAt(ceWorryingSiren = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notWorryingSound], Remaining, T).

initiatedAt(ceWorryingSiren = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([safeEnv], Remaining, T).

sdFluent( aux ).
