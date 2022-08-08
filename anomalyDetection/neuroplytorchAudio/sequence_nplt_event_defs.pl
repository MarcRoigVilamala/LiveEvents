atTime(X, X).

wrapper(X, Y) :- neuroplytorchAudio(Y, X).

neuroplytorchAudio(u_, -1). % Ignore this, it is just to define the format for the neuroplytorchAudio clause

% Number of timestamps to look at (should be min the length of the sequence)
givenWindowNeuroplytorchInit(1).
givenWindowNeuroplytorchTerm(2).

initiatedAt(ceNplytAirConditioner = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytAirConditioner], Window, T).

initiatedAt(ceNplytAirConditioner = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytAirConditioner)], Window, T).

initiatedAt(ceNplytCarHorn = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytCarHorn], Window, T).

initiatedAt(ceNplytCarHorn = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytCarHorn)], Window, T).

initiatedAt(ceNplytChildrenPlaying = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytChildrenPlaying], Window, T).

initiatedAt(ceNplytChildrenPlaying = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytChildrenPlaying)], Window, T).

initiatedAt(ceNplytDogBark = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytDogBark], Window, T).

initiatedAt(ceNplytDogBark = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytDogBark)], Window, T).

initiatedAt(ceNplytDrilling = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytDrilling], Window, T).

initiatedAt(ceNplytDrilling = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytDrilling)], Window, T).

initiatedAt(ceNplytEngineIdling = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytEngineIdling], Window, T).

initiatedAt(ceNplytEngineIdling = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytEngineIdling)], Window, T).

initiatedAt(ceNplytGunShot = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytGunShot], Window, T).

initiatedAt(ceNplytGunShot = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytGunShot)], Window, T).

initiatedAt(ceNplytJackhammer = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytJackhammer], Window, T).

initiatedAt(ceNplytJackhammer = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytJackhammer)], Window, T).

initiatedAt(ceNplytSiren = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytSiren], Window, T).

initiatedAt(ceNplytSiren = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytSiren)], Window, T).

initiatedAt(ceNplytStreetMusic = true, T) :-
    givenWindowNeuroplytorchInit(Window),
    sequence([outNplytStreetMusic], Window, T).

initiatedAt(ceNplytStreetMusic = false, T) :-
    givenWindowNeuroplytorchTerm(Window),
    sequence([exclude(outNplytStreetMusic)], Window, T).

sdFluent( aux ).
