
class teks(str):
    def __init__(self, chrs='', /):
        self._chrs = str(chrs)
    
    def kapitalkan(self, /):
        return self._chrs.capitalize()
    
    def simpul(self, /):
        return self._chrs.casefold()
    
    def ditengah(self, panjang, pengisi=' ', /):
        return self._chrs.center(panjang, pengisi)
    
    def hitung(self, args, /):
        if isinstance(args, str):
            return self._chrs.count(args)
        elif isinstance(args, (list, set, tuple)):
            result = []
            for arg in args:
                if not isinstance(arg, str):
                    raise TypeError(f"must be str, not {type(arg).__name__}")
                result.append(self._chrs(arg))
            return result
        else:
            raise TypeError(f"must be str, not {type(arg).__name__}")
    
    def diakhiri(self, )