% ==========================================
%       SIMPLE ADVANCED CALCULATOR
% ==========================================


% ------------------------------
% Addition
% ------------------------------

add(X, Y, Result) :-
    Result is X + Y.


% ------------------------------
% Subtraction
% ------------------------------

subtract(X, Y, Result) :-
    Result is X - Y.


% ------------------------------
% Multiplication
% ------------------------------

multiply(X, Y, Result) :-
    Result is X * Y.


% ------------------------------
% Division
% ------------------------------

divide(X, Y, Result) :-
    Y =\= 0,
    Result is X / Y.


% ------------------------------
% Modulus / Remainder
% ------------------------------

modulus(X, Y, Result) :-
    Y =\= 0,
    Result is X mod Y.


% ------------------------------
% Power
% ------------------------------

power(X, Y, Result) :-
    Result is X ** Y.


% ------------------------------
% Square
% ------------------------------

square(X, Result) :-
    Result is X * X.


% ------------------------------
% Cube
% ------------------------------

cube(X, Result) :-
    Result is X * X * X.


% ------------------------------
% Absolute Value
% ------------------------------

absolute(X, Result) :-
    Result is abs(X).


% ------------------------------
% Maximum of Two Numbers
% ------------------------------

maximum(X, Y, X) :-
    X >= Y.

maximum(X, Y, Y) :-
    Y > X.


% ------------------------------
% Minimum of Two Numbers
% ------------------------------

minimum(X, Y, X) :-
    X =< Y.

minimum(X, Y, Y) :-
    Y < X.


% ------------------------------
% Even Number Check
% ------------------------------

even(X) :-
    X mod 2 =:= 0.


% ------------------------------
% Odd Number Check
% ------------------------------

odd(X) :-
    X mod 2 =\= 0.


% ------------------------------
% Positive Number Check
% ------------------------------

positive(X) :-
    X > 0.


% ------------------------------
% Negative Number Check
% ------------------------------

negative(X) :-
    X < 0.



% ==========================================
%             EXAMPLE QUERIES
% ==========================================

% NOTE:
% In SWISH, put these queries in the QUERY box.
% Do not remove the % signs if you paste them
% inside the main program.


% ------------------------------
% Addition Queries
% ------------------------------

% ?- add(10, 5, Result).
% Result = 15.

% ?- add(20, 30, Result).
% Result = 50.


% ------------------------------
% Subtraction Queries
% ------------------------------

% ?- subtract(10, 5, Result).
% Result = 5.

% ?- subtract(50, 20, Result).
% Result = 30.


% ------------------------------
% Multiplication Queries
% ------------------------------

% ?- multiply(10, 5, Result).
% Result = 50.

% ?- multiply(7, 8, Result).
% Result = 56.


% ------------------------------
% Division Queries
% ------------------------------

% ?- divide(20, 4, Result).
% Result = 5.

% ?- divide(15, 2, Result).
% Result = 7.5.


% Division by zero will fail:
% ?- divide(10, 0, Result).
% false.


% ------------------------------
% Modulus Queries
% ------------------------------

% ?- modulus(10, 3, Result).
% Result = 1.

% ?- modulus(20, 6, Result).
% Result = 2.


% ------------------------------
% Power Queries
% ------------------------------

% ?- power(2, 3, Result).
% Result = 8.

% ?- power(5, 2, Result).
% Result = 25.


% ------------------------------
% Square Queries
% ------------------------------

% ?- square(5, Result).
% Result = 25.

% ?- square(10, Result).
% Result = 100.


% ------------------------------
% Cube Queries
% ------------------------------

% ?- cube(3, Result).
% Result = 27.

% ?- cube(5, Result).
% Result = 125.


% ------------------------------
% Absolute Value Queries
% ------------------------------

% ?- absolute(-15, Result).
% Result = 15.

% ?- absolute(20, Result).
% Result = 20.


% ------------------------------
% Maximum Queries
% ------------------------------

% ?- maximum(20, 35, Result).
% Result = 35.

% ?- maximum(50, 10, Result).
% Result = 50.

% ?- maximum(20, 20, Result).
% Result = 20.


% ------------------------------
% Minimum Queries
% ------------------------------

% ?- minimum(20, 35, Result).
% Result = 20.

% ?- minimum(50, 10, Result).
% Result = 10.

% ?- minimum(20, 20, Result).
% Result = 20.


% ------------------------------
% Even Number Queries
% ------------------------------

% ?- even(10).
% true.

% ?- even(7).
% false.


% ------------------------------
% Odd Number Queries
% ------------------------------

% ?- odd(7).
% true.

% ?- odd(10).
% false.


% ------------------------------
% Positive Number Queries
% ------------------------------

% ?- positive(15).
% true.

% ?- positive(-5).
% false.


% ------------------------------
% Negative Number Queries
% ------------------------------

% ?- negative(-5).
% true.

% ?- negative(10).
% false.


% ==========================================
%        SOME MORE PRACTICE QUERIES
% ==========================================

% ?- add(100, 50, X).

% ?- subtract(100, 35, X).

% ?- multiply(12, 12, X).

% ?- divide(100, 4, X).

% ?- modulus(17, 5, X).

% ?- power(3, 4, X).

% ?- square(12, X).

% ?- cube(4, X).

% ?- absolute(-100, X).

% ?- maximum(45, 78, X).

% ?- minimum(45, 78, X).

% ?- even(100).

% ?- odd(99).

% ?- positive(50).

% ?- negative(-25).