% =========================================================
%       FAMILY RELATIONSHIP EXPERT SYSTEM IN PROLOG
% =========================================================


% ---------------------------------------------------------
% 1. FACTS: GENDER
% ---------------------------------------------------------

male(rahim).
male(karim).
male(hasan).
male(rakib).

female(fatema).
female(salma).
female(riya).
female(mim).


% ---------------------------------------------------------
% 2. FACTS: PARENT RELATIONSHIPS
% parent(Parent, Child).
% ---------------------------------------------------------

parent(rahim, karim).
parent(fatema, karim).

parent(rahim, salma).
parent(fatema, salma).

parent(karim, rakib).
parent(riya, rakib).

parent(salma, mim).
parent(hasan, mim).


% ---------------------------------------------------------
% 3. FACTS: MARRIAGE
% married(Husband, Wife).
% ---------------------------------------------------------

married(rahim, fatema).
married(karim, riya).
married(hasan, salma).


% =========================================================
%                       RULES
% =========================================================


% ---------------------------------------------------------
% Father
% ---------------------------------------------------------

father(X, Y) :-
    male(X),
    parent(X, Y).


% ---------------------------------------------------------
% Mother
% ---------------------------------------------------------

mother(X, Y) :-
    female(X),
    parent(X, Y).


% ---------------------------------------------------------
% Child
% child(X, Y) means X is a child of Y
% ---------------------------------------------------------

child(X, Y) :-
    parent(Y, X).


% ---------------------------------------------------------
% Son
% ---------------------------------------------------------

son(X, Y) :-
    male(X),
    parent(Y, X).


% ---------------------------------------------------------
% Daughter
% ---------------------------------------------------------

daughter(X, Y) :-
    female(X),
    parent(Y, X).


% ---------------------------------------------------------
% Brother
% ---------------------------------------------------------

brother(X, Y) :-
    male(X),
    parent(P, X),
    parent(P, Y),
    X \= Y.


% ---------------------------------------------------------
% Sister
% ---------------------------------------------------------

sister(X, Y) :-
    female(X),
    parent(P, X),
    parent(P, Y),
    X \= Y.


% ---------------------------------------------------------
% Sibling
% ---------------------------------------------------------

sibling(X, Y) :-
    parent(P, X),
    parent(P, Y),
    X \= Y.


% ---------------------------------------------------------
% Husband
% ---------------------------------------------------------

husband(X, Y) :-
    male(X),
    married(X, Y).


% ---------------------------------------------------------
% Wife
% ---------------------------------------------------------

wife(X, Y) :-
    female(X),
    married(Y, X).


% ---------------------------------------------------------
% Grandfather
% ---------------------------------------------------------

grandfather(X, Y) :-
    male(X),
    parent(X, Z),
    parent(Z, Y).


% ---------------------------------------------------------
% Grandmother
% ---------------------------------------------------------

grandmother(X, Y) :-
    female(X),
    parent(X, Z),
    parent(Z, Y).


% ---------------------------------------------------------
% Grandparent
% ---------------------------------------------------------

grandparent(X, Y) :-
    parent(X, Z),
    parent(Z, Y).


% ---------------------------------------------------------
% Uncle
% ---------------------------------------------------------

uncle(X, Y) :-
    brother(X, P),
    parent(P, Y).


% ---------------------------------------------------------
% Aunt
% ---------------------------------------------------------

aunt(X, Y) :-
    sister(X, P),
    parent(P, Y).


% ---------------------------------------------------------
% Nephew
% nephew(X, Y) means X is nephew of Y
% ---------------------------------------------------------

nephew(X, Y) :-
    male(X),
    parent(P, X),
    sibling(P, Y).


% ---------------------------------------------------------
% Niece
% niece(X, Y) means X is niece of Y
% ---------------------------------------------------------

niece(X, Y) :-
    female(X),
    parent(P, X),
    sibling(P, Y).


% ---------------------------------------------------------
% Cousin
% ---------------------------------------------------------

cousin(X, Y) :-
    parent(P1, X),
    parent(P2, Y),
    sibling(P1, P2),
    X \= Y.


% ---------------------------------------------------------
% Ancestor
% Direct parent is an ancestor
% ---------------------------------------------------------

ancestor(X, Y) :-
    parent(X, Y).


% Recursive ancestor rule
ancestor(X, Y) :-
    parent(X, Z),
    ancestor(Z, Y).


% =========================================================
%                  EXAMPLE QUERIES
% =========================================================

% NOTE:
% Do NOT paste "?-" queries inside the program editor in SWISH.
% Put them in the QUERY box one at a time.


% -------------------------
% Gender Queries
% -------------------------

% Find all males:
% ?- male(X).

% Find all females:
% ?- female(X).

% Check if Rakib is male:
% ?- male(rakib).

% Check if Mim is female:
% ?- female(mim).


% -------------------------
% Parent Queries
% -------------------------

% Find all parent relationships:
% ?- parent(X, Y).

% Find parents of Rakib:
% ?- parent(X, rakib).

% Find parents of Mim:
% ?- parent(X, mim).

% Find children of Rahim:
% ?- parent(rahim, X).

% Find children of Fatema:
% ?- parent(fatema, X).


% -------------------------
% Father Queries
% -------------------------

% Find all fathers:
% ?- father(X, Y).

% Find Karim's father:
% ?- father(X, karim).

% Find Salma's father:
% ?- father(X, salma).

% Find Rakib's father:
% ?- father(X, rakib).

% Find Mim's father:
% ?- father(X, mim).

% Find Rahim's children:
% ?- father(rahim, X).


% -------------------------
% Mother Queries
% -------------------------

% Find all mothers:
% ?- mother(X, Y).

% Find Karim's mother:
% ?- mother(X, karim).

% Find Salma's mother:
% ?- mother(X, salma).

% Find Rakib's mother:
% ?- mother(X, rakib).

% Find Mim's mother:
% ?- mother(X, mim).


% -------------------------
% Child Queries
% -------------------------

% Find all children and their parents:
% ?- child(X, Y).

% Find children of Rahim:
% ?- child(X, rahim).

% Find children of Fatema:
% ?- child(X, fatema).

% Find children of Karim:
% ?- child(X, karim).

% Find children of Salma:
% ?- child(X, salma).


% -------------------------
% Son Queries
% -------------------------

% Find all son relationships:
% ?- son(X, Y).

% Find Rahim's sons:
% ?- son(X, rahim).

% Find Karim's sons:
% ?- son(X, karim).


% -------------------------
% Daughter Queries
% -------------------------

% Find all daughter relationships:
% ?- daughter(X, Y).

% Find Rahim's daughters:
% ?- daughter(X, rahim).

% Find Salma's daughters:
% ?- daughter(X, salma).


% -------------------------
% Brother Queries
% -------------------------

% Find all brother relationships:
% ?- brother(X, Y).

% Find Salma's brother:
% ?- brother(X, salma).

% Check whether Karim is Salma's brother:
% ?- brother(karim, salma).


% -------------------------
% Sister Queries
% -------------------------

% Find all sister relationships:
% ?- sister(X, Y).

% Find Karim's sister:
% ?- sister(X, karim).

% Check whether Salma is Karim's sister:
% ?- sister(salma, karim).


% -------------------------
% Sibling Queries
% -------------------------

% Find all siblings:
% ?- sibling(X, Y).

% Find Karim's siblings:
% ?- sibling(X, karim).

% Find Salma's siblings:
% ?- sibling(X, salma).


% -------------------------
% Husband Queries
% -------------------------

% Find all husbands:
% ?- husband(X, Y).

% Find Fatema's husband:
% ?- husband(X, fatema).

% Find Riya's husband:
% ?- husband(X, riya).

% Find Salma's husband:
% ?- husband(X, salma).


% -------------------------
% Wife Queries
% -------------------------

% Find all wives:
% ?- wife(X, Y).

% Find Rahim's wife:
% ?- wife(X, rahim).

% Find Karim's wife:
% ?- wife(X, karim).

% Find Hasan's wife:
% ?- wife(X, hasan).


% -------------------------
% Grandfather Queries
% -------------------------

% Find all grandfather relationships:
% ?- grandfather(X, Y).

% Find Rakib's grandfather:
% ?- grandfather(X, rakib).

% Find Mim's grandfather:
% ?- grandfather(X, mim).

% Find grandchildren of Rahim:
% ?- grandfather(rahim, X).


% -------------------------
% Grandmother Queries
% -------------------------

% Find all grandmother relationships:
% ?- grandmother(X, Y).

% Find Rakib's grandmother:
% ?- grandmother(X, rakib).

% Find Mim's grandmother:
% ?- grandmother(X, mim).

% Find grandchildren of Fatema:
% ?- grandmother(fatema, X).


% -------------------------
% Grandparent Queries
% -------------------------

% Find all grandparents:
% ?- grandparent(X, Y).

% Find Rakib's grandparents:
% ?- grandparent(X, rakib).

% Find Mim's grandparents:
% ?- grandparent(X, mim).


% -------------------------
% Uncle Queries
% -------------------------

% Find all uncle relationships:
% ?- uncle(X, Y).

% Find Mim's uncle:
% ?- uncle(X, mim).

% Check if Karim is Mim's uncle:
% ?- uncle(karim, mim).


% -------------------------
% Aunt Queries
% -------------------------

% Find all aunt relationships:
% ?- aunt(X, Y).

% Find Rakib's aunt:
% ?- aunt(X, rakib).

% Check if Salma is Rakib's aunt:
% ?- aunt(salma, rakib).


% -------------------------
% Nephew Queries
% -------------------------

% Find all nephew relationships:
% ?- nephew(X, Y).

% Find Salma's nephew:
% ?- nephew(X, salma).

% Check if Rakib is Salma's nephew:
% ?- nephew(rakib, salma).


% -------------------------
% Niece Queries
% -------------------------

% Find all niece relationships:
% ?- niece(X, Y).

% Find Karim's niece:
% ?- niece(X, karim).

% Check if Mim is Karim's niece:
% ?- niece(mim, karim).


% -------------------------
% Cousin Queries
% -------------------------

% Find all cousins:
% ?- cousin(X, Y).

% Find Rakib's cousin:
% ?- cousin(rakib, X).

% Find Mim's cousin:
% ?- cousin(mim, X).

% Check if Rakib and Mim are cousins:
% ?- cousin(rakib, mim).

% Check reverse relationship:
% ?- cousin(mim, rakib).


% -------------------------
% Ancestor Queries
% -------------------------

% Find all ancestor relationships:
% ?- ancestor(X, Y).

% Find all ancestors of Rakib:
% ?- ancestor(X, rakib).

% Find all ancestors of Mim:
% ?- ancestor(X, mim).

% Find descendants of Rahim:
% ?- ancestor(rahim, X).

% Check whether Rahim is Rakib's ancestor:
% ?- ancestor(rahim, rakib).

% Check whether Fatema is Mim's ancestor:
% ?- ancestor(fatema, mim).