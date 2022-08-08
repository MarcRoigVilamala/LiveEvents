% nn(sound_net,[X],Y,[boom, siren, silence, gun_shot, shatter, screaming, engine_idling, car_horn, jackhammer, street_music]) :: sound(X,Y).
% nn(sound_net,[X],Y,[boom, siren, silence, gun_shot, shatter, screaming]) :: sound(X,Y).
% nn(sound_net,[X],Y,[boom, silence, gun_shot, shatter, screaming]) :: sound(X,Y).

wrapper(X, Y) :- sound(X, Y).

wrapper(X, explosion) :- wrapper(X, boom).
wrapper(X, explosion) :- wrapper(X, gun_shot).

atTime(T, A) :- atTimeAudio(T, A).

sound(-1, u_). % Ignore this, it is just to define the format for the sound clause

isNegation(notScreaming, screaming).
isNegation(notShatter, shatter).
isNegation(notGunShot, gun_shot).
isNegation(notSilence, silence).

% Number of timestamps to look at (should be min the length of the sequence)
givenRemaining(5).

initiatedAt(single = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notSilence], Remaining, T),
    sequenceEndingAt([explosion, explosion], Remaining, T).

initiatedAt(single = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notScreaming], Remaining, T),
    sequenceEndingAt([notShatter], Remaining, T),
    sequenceEndingAt([notGunShot], Remaining, T).


initiatedAt(chained = true, T) :-
    allTimeStamps(Timestamps),
    previousTimeStampN(T, Timestamps, Tprev, 3),
    initiatedAt(single = true, Tprev),
    givenRemaining(Remaining),
    sequenceEndingAt([notSilence], Remaining, T),
    sequenceEndingAt([explosion, explosion], Remaining, T).

initiatedAt(chained = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([notScreaming], Remaining, T),
    sequenceEndingAt([notShatter], Remaining, T),
    sequenceEndingAt([notGunShot], Remaining, T).


initiatedAt(training = true, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([silence, explosion, explosion], Remaining, T).

initiatedAt(training = false, T) :-
    givenRemaining(Remaining),
    sequenceEndingAt([siren, siren], Remaining, T).

sdFluent( aux ).
