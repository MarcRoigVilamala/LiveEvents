% Main interface for the framework.
sequence(L, W, T) :-
    reverse(L, L2), % Reverse list to simplify rule definitions
    sequenceEndingAt(L2, W, T).

% Add element X at the tail of the list
add_tail([], X, [X]).
add_tail([H | T], X, [H | L]) :- add_tail(T, X, L).

% The second list is the reverse of the first
reverse([], []).
reverse([X], [X]).
reverse([X | Xs], R) :-
    reverse(Xs, T),
    add_tail(T, X, R).

% This allows the use of exclude(X) to not allow certain simple events in the middle of the sequence
isNegation(exclude(X), X).

% Example of the structure of wraps. Added to prevent errors where wraps is not defined
wraps(thisShouldNotBeUsedWrapper, thisShouldNotBeUsedWrapped).

% Defining happensAt using atTime and wrapper
happensAt(X, T) :-
    atTime(T, A),
    wrapper(A, X).

% This allows the user to define how a keyword can wrap another
wrapper(X, N1) :- wraps(N1, N2), wrapper(X, N2).

% These rules allow the user to detect if an item has been excluded.
itemInExcluded(X, [X | _]).
% The rule below prevents instances of the wrapper triggering the excluded clause. For example, if we have a rule
% excluding instances of "dog" (that is Y=dog), and wraps(animal, dog) is true, any timestamp for which
% happensAt(dog, T) is true will also generate a happensAt(animal, T). This will result in evaluating the clause
% itemInExcluded(dog, [dog | _]), which will be true (and thus the sequence will be false, as it should). However,
% including the wraps(animal, dog) will generate the happensAt(animal, T) simple event, which will cause the system to
% evaluate itemInExcluded(animal, [dog | _]) which will be false (assuming that animal has not been excluded as well).
% This will cause the sequence to be true, which should not happen as the only base simple event that has happened is
% "dog", which has been excluded. If we do not want the addition of wraps(animal, dog) to break this interaction, the
% rule below needs to be added.
itemInExcluded(X, [Y | _]) :- wraps(X, Y).
% Same as above but the other way round
itemInExcluded(X, [Y | _]) :- wraps(Y, X).
itemInExcluded(X, [_ | L]) :- itemInExcluded(X, L).

% Check that Y is not in the list of excluded E
checkExcluded(Y, E) :- \+ itemInExcluded(Y, E).

% An empty sequence will always be within if there are no simple events excluded
sequenceWithin([], [], _, _).

% An empty sequence will also be within if we have used all of the Remaining
sequenceWithin([], _, 0, _).

% An empty sequence will also be within if we reach the start of the timeline
sequenceWithin([], _, _, 0).

sequenceWithin([], E, Remaining, T) :-
    Remaining > 0,
    happensAt(Y, T),
    checkExcluded(Y, E),
    NextRemaining is Remaining - 1,
    allTimeStamps(Timestamps),
    previousTimeStamp(T, Timestamps, Tprev),
    sequenceWithin([], E, NextRemaining, Tprev).

% A sequence can be within Remaining of T if it starts at T
sequenceWithin(L, E, Remaining, T) :-
    sequenceEndingAt(L, Remaining, T).

sequenceWithin([X | L], E, Remaining, T) :-
    isNegation(X, Y),
    sequenceWithin(L, [Y | E], Remaining, T).

% A sequence can be within Remaining of T if it is within NextRemaining of Tprev
sequenceWithin([X | L], E, Remaining, T) :-
    Remaining > 0,
    T >= 0,
    \+ isNegation(X, _),
    happensAt(Y, T),
    checkExcluded(Y, E),
    NextRemaining is Remaining - 1,
    allTimeStamps(Timestamps),
    previousTimeStamp(T, Timestamps, Tprev),
    sequenceWithin([X | L], E, NextRemaining, Tprev).

% A sequence will start at T and be within Remaining if X happens at T and the rest of the sequence is within NextRemaining of Tprev
sequenceEndingAt([X | L], Remaining, T) :-
    Remaining > 0,
    T >= 0,
    \+ isNegation(X, _),
    happensAt(X, T),
    NextRemaining is Remaining - 1,
    allTimeStamps(Timestamps),
    previousTimeStamp(T, Timestamps, Tprev),
    sequenceWithin(L, [], NextRemaining, Tprev).

sequenceEndingAt([X | L], Remaining, T) :-
    Remaining > 0,
    T >= 0,
    isNegation(X, _),
    sequenceWithin([X | L], [], Remaining, T).
