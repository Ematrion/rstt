'''NOTE:
        1. Implementation choice
            - Standing is an hybrid of container/iterable. It belongs to the Collections categorie as a list and dictionary.
            - It is a list, a defaultdict (key, value ) and a 'symetrical dictionary' (key, index) <-> (index, key)
            - A double implemntation (self._list and self._dict) makes many features easy and safer to implement.
            However the duplication of a data becomes a massif issue regarding synchronization and memory usage.
            - self.ranks as a List[Tuple[key, value]] as many down side, especialy because tuple are immutable.
            However it as a clarity upside: We have a list of key-value pairs.
            There are 2 explicit field, one for key, one for value.
            Items are contained in a list which implicitly assigned them an index.
            And the class build itself upon the list features.
            The dictionary-like interface needed more work arround.

        TODO:

        1. KEY type
            * Generalize Standing based on a key_type
            * Typehint should support the key_type in the method signature
            * ISSUE: 
                - key can not be an int, because it would have ambigous behaviour with index
                - should key_type be of different of a potential value_type
                - key_type would impact the second key for self.ranks.sort() in c.f. __sort()

            A naive implementation based on self.key_type will not work
            as self.key_type is not defined in a function signature

            Try with Generic[key_type] or Generic[key_type, value_type]
            which one should be comparable ? only value or both ?

            Depending on the implement choice __setitem__() can have symetrical behaviour with __getitem__()

        2. Sorting Policy
            * in __init__() define a sorting self.policy with
            functools.cmp_to_key : https://docs.python.org/3/library/functools.html#functools.cmp_to_key

        3. Typing Hints
            * decorate with @typechecked where needed
            * but without overusing it - ONLY where needed

        4. only_sorted_method 
            * some getter and setter do not make any sense when self.__sorted is False
            * a decorator raising error/warnings based on __sorted/_keep_sorted 

            for example pop() makes no sense when not sorted, remove() should be used in that case. 

        5. Handle __sort() calls
            * Optimizing the class performance is crucial
            * python list.sort() is optimized but remains costy on large list
            * Ideas:
                - call on either setter/getter only
                - optimal sorting algorithm explicit call based on self.ranks methods impact (local/global changes)
                - self._safety_ in ['set', 'get', 'all']

            Goal is to minimize calls that guarantee the expected behaviour.
            It also needs clear Warnings and Exception raised based (cf 3)
            But the optimized approach depends on the use case:
                - Is the Standing use to hold frequently updated values ?
                - Is it used to order automaticly items ?

            The _safety_ approach moves part of the issue to the responsability of the user
            thus add flexibility to class 'reasonable' applications.

        6. full documentation
            * for user
            * for develloper

        7. Classmethod
            * rerank() and fit() could be done as classmethod
            * idealy they are implemented such that any inherited class work as intended

        8. Terminology
            * Consistency in wording for parameters and documentation
            * do we talk about keys or player, do we use index or rank ?

        9. isinstance()
            * extremly used in __{set/del/get}item__ methods
            * is it necessary, is it the best practice ?

            The reason is the list & dict behaviour implement different interfaces based on types    

        :meta private:  
        '''
