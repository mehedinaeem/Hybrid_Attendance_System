% ---------- Facts ----------

male(rahim).
male(karim).
male(hasan).
male(rakib).

female(fatema).
female(salma).
female(riya).
female(mim).

parent(rahim, karim).
parent(fatema, karim).

parent(rahim, salma).
parent(fatema, salma).

parent(karim, rakib).
parent(riya, rakib).

parent(salma, mim).
parent(hasan, mim).


% ---------- Rules ----------

father(X, Y) :-
    male(X),
    parent(X, Y).

mother(X, Y) :-
    female(X),
    parent(X, Y).

brother(X, Y) :-
    male(X),
    parent(P, X),
    parent(P, Y),
    X \= Y.

sister(X, Y) :-
    female(X),
    parent(P, X),
    parent(P, Y),
    X \= Y.


grandfather(X, Y) :-
    male(X),
    parent(X, Z),
    parent(Z, Y).

grandmother(X, Y) :-
    female(X),
    parent(X, Z),
    parent(Z, Y).

uncle(X, Y) :-
    brother(X, P),
    parent(P, Y).

aunt(X, Y) :-
    sister(X, P),
    parent(P, Y).

cousin(X, Y) :-
    parent(P1, X),
    parent(P2, Y),
    parent(G, P1),
    parent(G, P2),
    P1 \= P2.