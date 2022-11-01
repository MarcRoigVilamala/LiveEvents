atTime(X, X).
nlp(-1, _u). % Ignore this, it is just to define the format for the nlp clause

wrapper(X, Y) :- nlp(X, Y).

wraps(banOffence, ishate).

wraps(banOffence, national_origin).

wraps(banOffence, violence).
wraps(banOffence, gender).
wraps(banOffence, race).
wraps(banOffence, disability).
wraps(banOffence, religion).
wraps(banOffence, sexual_orientation).

% Number of timestamps to look at (should be min the length of the sequence)
givenWindow(2).

initiatedAt(ceBan = true, T) :-
    givenWindow(Window),
    sequence([banOffence, banOffence], Window, T).

initiatedAt(ceBan = false, T) :-
    givenWindow(Window),
    sequence([exclude(banOffence)], Window, T).
