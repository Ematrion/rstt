''' 
    Ranking Class Comment
    ---------------------
    
    NOTE:
        - The Ranking class has two dict[Player, ...], (RatingSystem, Standing) - which induce redundancy and ambiguity.
        The 'Container Equivalence' and 'Rank Disambiguity' (SEE GLOSSARY) are two properties that needs to be enforced
        to guarantee a well defined behaviour for the Ranking class. Hopefully it is also sufficient.

        - The RatingSystem act like a defaultdict. Get operations can induce set operations.
        This is tricky as a player could be inserted in the ranking using 'read' methods of the interface.

    GLOSSARY:
        - Container Equivalence (Union == Intersection):
        (key in self.datamodel.ratings) <=> (key in self.standing).
        In the code we refer to 'equivalence'

        - Rank Disambiguity (point '=' rating):
        self.datamodel.ordinal(key) == self.standing.value(key) for all keys.
        In the code we refer to 'disambiguity'

    # !!!
        - self.__disambiguity == True && self._Standing__sorted == False
        This means that the players have the correct points but are not correctly ranked.
        It can happen when 'self.standing._keep_sorted_ == False' which is triggered by the user outside of the Ranking methods.

    # ???
        - Can this state be reached from the intended Ranking usage ?
        How to detect it and what to do ?
        => What is the ranking class responsability in this contexte?
    '''
