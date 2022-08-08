atTime(X, X).

wrapper(X, Y) :- sound(X, Y).

sound(-1, u_). % Ignore this, it is just to define the format for the sound clause

isNegation(notSilence, silence).
isNegation(notSpeech, speech).

% Number of timestamps to look at (should be min the length of the sequence)
windowStart(10).
windowEnd(2).

initiatedAt(ceSilence = true, T) :-
    windowStart(Window),
    sequence([silence, silence, silence], Window, T).

initiatedAt(ceSilence = false, T) :-
    windowEnd(Window),
    sequence([notSilence], Window, T).

initiatedAt(ceSpeech = true, T) :-
    windowStart(Window),
    sequenceEndingAt([speech, speech, speech], Window, T).

initiatedAt(ceSpeech = false, T) :-
    windowEnd(Window),
    sequence([notSpeech], Window, T).

sdFluent( aux ).
