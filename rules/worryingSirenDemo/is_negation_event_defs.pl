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
    sequence([airConditioner, airConditioner], Remaining, T).

initiatedAt(ceAirConditioner = false, T) :-
    givenRemaining(Remaining),
    sequence([notAirConditioner], Remaining, T).

initiatedAt(ceCarHorn = true, T) :-
    givenRemaining(Remaining),
    sequence([carHorn, carHorn], Remaining, T).

initiatedAt(ceCarHorn = false, T) :-
    givenRemaining(Remaining),
    sequence([notCarHorn], Remaining, T).

initiatedAt(ceChildrenPlaying = true, T) :-
    givenRemaining(Remaining),
    sequence([childrenPlaying, childrenPlaying], Remaining, T).

initiatedAt(ceChildrenPlaying = false, T) :-
    givenRemaining(Remaining),
    sequence([notChildrenPlaying], Remaining, T).

initiatedAt(ceDogBark = true, T) :-
    givenRemaining(Remaining),
    sequence([dogBark, dogBark], Remaining, T).

initiatedAt(ceDogBark = false, T) :-
    givenRemaining(Remaining),
    sequence([notDogBark], Remaining, T).

initiatedAt(ceDrilling = true, T) :-
    givenRemaining(Remaining),
    sequence([drilling, drilling], Remaining, T).

initiatedAt(ceDrilling = false, T) :-
    givenRemaining(Remaining),
    sequence([notDrilling], Remaining, T).

initiatedAt(ceEngineIdling = true, T) :-
    givenRemaining(Remaining),
    sequence([engineIdling, engineIdling], Remaining, T).

initiatedAt(ceEngineIdling = false, T) :-
    givenRemaining(Remaining),
    sequence([notEngineIdling], Remaining, T).

initiatedAt(ceGunShot = true, T) :-
    givenRemaining(Remaining),
    sequence([gunShot, gunShot], Remaining, T).

initiatedAt(ceGunShot = false, T) :-
    givenRemaining(Remaining),
    sequence([notGunShot], Remaining, T).

initiatedAt(ceJackhammer = true, T) :-
    givenRemaining(Remaining),
    sequence([jackhammer, jackhammer], Remaining, T).

initiatedAt(ceJackhammer = false, T) :-
    givenRemaining(Remaining),
    sequence([notJackhammer], Remaining, T).

initiatedAt(ceSiren = true, T) :-
    givenRemaining(Remaining),
    sequence([siren, siren], Remaining, T).

initiatedAt(ceSiren = false, T) :-
    givenRemaining(Remaining),
    sequence([notSiren], Remaining, T).

initiatedAt(ceStreetMusic = true, T) :-
    givenRemaining(Remaining),
    sequence([streetMusic, streetMusic], Remaining, T).

initiatedAt(ceStreetMusic = false, T) :-
    givenRemaining(Remaining),
    sequence([notStreetMusic], Remaining, T).

%initiatedAt(ceWorryingSiren = true, T) :-
%    givenRemaining(Remaining),
%    sequenceEndingAt([notSafeEnv, siren, notSafeEnv, siren, notSafeEnv, siren, safeEnv], Remaining, T).

initiatedAt(ceWorryingSiren = true, T) :-
    givenRemaining(Remaining),
    sequence([safeEnv, siren, notSafeEnv, siren, notSafeEnv, siren, notSafeEnv], Remaining, T).

initiatedAt(ceWorryingSiren = true, T) :-
    givenRemaining(Remaining),
    allTimeStamps(Timestamps),
    previousTimeStamp(T, Timestamps, Tprev),
    holdsAt_(ceWorryingSiren = true, Tprev),
    sequence([notSafeEnv], Remaining, T),
    sequence([worryingSound, worryingSound], Remaining, T).

initiatedAt(ceWorryingSiren = false, T) :-
    givenRemaining(Remaining),
    sequence([notWorryingSound], Remaining, T).

initiatedAt(ceWorryingSiren = false, T) :-
    givenRemaining(Remaining),
    sequence([safeEnv], Remaining, T).

sdFluent( aux ).
