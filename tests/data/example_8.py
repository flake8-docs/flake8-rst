class Test:

    def _cvc(self, i):
        """Check if b[j - 2: j + 1] makes the (consonant, vowel, consonant) pattern and also
        if the second 'c' is not 'w', 'x' or 'y'. This is used when trying to restore an 'e' at the end of a short word,
        e.g. cav(e), lov(e), hop(e), crim(e), but snow, box, tray.

        Parameters
        ----------
        i : int
            Index for `b`

        Returns
        -------
        bool

        Examples
        --------
        .. sourcecode:: pycon

            >>> from gensim.parsing.porter import PorterStemmer
            >>> p = PorterStemmer()
            >>> p.b = "lib"
            >>> p.j = 2
            >>> p._cvc(2)
            True

            >>> from gensim.parsing.porter import PorterStemmer
            >>> p = PorterStemmer()
            >>> p.b = "dll"
            >>> p.j = 2
            >>> p._cvc(2)
            False

            >>> from gensim.parsing.porter import PorterStemmer
            >>> p = PorterStemmer()
            >>> p.b = "wow"
            >>> p.j = 2
            >>> p._cvc(2)
            False

        """
        if i < 2 or not self._cons(i) or self._cons(i - 1) or not self._cons(i - 2):
            return False
        return self.b[i] not in "wxy"
