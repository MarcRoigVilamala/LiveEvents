atTime(X, X).

wrapper(X, Y) :- sound(X, Y).

wraps(safeEnv, childrenPlaying).
wraps(safeEnv, streetMusic).

wraps(worryingSound, gunShot).
wraps(worryingSound, siren).

sound(-1, u_). % Ignore this, it is just to define the format for the sound clause

% Number of timestamps to look at (should be min the length of the sequence)
givenWindow(10).

initiatedAt(ceAirConditioner = true, T) :-
    givenWindow(Window),
    sequence([airConditioner, airConditioner], Window, T).

initiatedAt(ceAirConditioner = false, T) :-
    givenWindow(Window),
    sequence([exclude(airConditioner)], Window, T).

initiatedAt(ceCarHorn = true, T) :-
    givenWindow(Window),
    sequence([carHorn, carHorn], Window, T).

initiatedAt(ceCarHorn = false, T) :-
    givenWindow(Window),
    sequence([exclude(carHorn)], Window, T).

initiatedAt(ceChildrenPlaying = true, T) :-
    givenWindow(Window),
    sequence([childrenPlaying, childrenPlaying], Window, T).

initiatedAt(ceChildrenPlaying = false, T) :-
    givenWindow(Window),
    sequence([exclude(childrenPlaying)], Window, T).

initiatedAt(ceDogBark = true, T) :-
    givenWindow(Window),
    sequence([dogBark, dogBark], Window, T).

initiatedAt(ceDogBark = false, T) :-
    givenWindow(Window),
    sequence([exclude(dogBark)], Window, T).

initiatedAt(ceDrilling = true, T) :-
    givenWindow(Window),
    sequence([drilling, drilling], Window, T).

initiatedAt(ceDrilling = false, T) :-
    givenWindow(Window),
    sequence([exclude(drilling)], Window, T).

initiatedAt(ceEngineIdling = true, T) :-
    givenWindow(Window),
    sequence([engineIdling, engineIdling], Window, T).

initiatedAt(ceEngineIdling = false, T) :-
    givenWindow(Window),
    sequence([exclude(engineIdling)], Window, T).

initiatedAt(ceGunShot = true, T) :-
    givenWindow(Window),
    sequence([gunShot, gunShot], Window, T).

initiatedAt(ceGunShot = false, T) :-
    givenWindow(Window),
    sequence([exclude(gunShot)], Window, T).

initiatedAt(ceJackhammer = true, T) :-
    givenWindow(Window),
    sequence([jackhammer, jackhammer], Window, T).

initiatedAt(ceJackhammer = false, T) :-
    givenWindow(Window),
    sequence([exclude(jackhammer)], Window, T).

initiatedAt(ceSiren = true, T) :-
    givenWindow(Window),
    sequence([siren, siren], Window, T).

initiatedAt(ceSiren = false, T) :-
    givenWindow(Window),
    sequence([exclude(siren)], Window, T).

initiatedAt(ceStreetMusic = true, T) :-
    givenWindow(Window),
    sequence([streetMusic, streetMusic], Window, T).

initiatedAt(ceStreetMusic = false, T) :-
    givenWindow(Window),
    sequence([exclude(streetMusic)], Window, T).

%initiatedAt(ceWorryingSiren = true, T) :-
%    givenWindow(Window),
%    sequenceEndingAt([exclude(safeEnv), siren, exclude(safeEnv), siren, exclude(safeEnv), siren, safeEnv], Window, T).

initiatedAt(ceWorryingSiren = true, T) :-
    givenWindow(Window),
    sequence([safeEnv, siren, exclude(safeEnv), siren, exclude(safeEnv), siren, exclude(safeEnv)], Window, T).

initiatedAt(ceWorryingSiren = true, T) :-
    givenWindow(Window),
    allTimeStamps(Timestamps),
    previousTimeStamp(T, Timestamps, Tprev),
    holdsAt_(ceWorryingSiren = true, Tprev),
    sequence([exclude(safeEnv)], Window, T),
    sequence([worryingSound, worryingSound], Window, T).

initiatedAt(ceWorryingSiren = false, T) :-
    givenWindow(Window),
    sequence([exclude(worryingSound)], Window, T).

initiatedAt(ceWorryingSiren = false, T) :-
    givenWindow(Window),
    sequence([safeEnv], Window, T).

sdFluent( aux ).
