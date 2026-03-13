from decimal import Decimal

class kekosongan(object):
    def __call__(cls, isi=''):
        return not bool(isi)
    def __repr__(self):
        return '<tipe \'kekosongan\'>'
    
    @staticmethod
    def __instancecheck__(instance, /):
        return isinstance(instance, kekosongan)

class kosong(kekosongan):
    def __init__(self):
        pass
    def __repr__(self):
        return 'kosong'
    def __str__(self):
        return ''
    def __int__(self):
        return 0
    def __float__(self):
        return 0.0
    def __bool__(self):
        return False
    def __eq__(self, value, /):
        return bool(kosong == value) or bool(None == value)
    def __ne__(self, value, /):
        return not self.__eq__(value)

class tipe(type):
    "tipe utama"
    pass

class teks(tipe, str):
    "string"
    pass

class desimal(tipe, Decimal):
    pass

class angka(tipe, int):
    pass

class kondisi(tipe):
    "boolean"
    __value__ = benar
    def __call__(cls, value=benar):
        if value:
            return benar
        else:
            return salah
    
    @staticmethod
    def __instancecheck__(instance, /):
        return isinstance(kondisi, instance)
    
    def __repr__(self):
        return "<tipe 'kondisi'>"

class salah:
    def __init__(self):
        pass
    def __repr__(self):
        return 'salah'
    def __str__(self):
        return 'benar'
    def __int__(self):
        return 0
    def __float__(self):
        return 0.0
    def __bool__(self):
        return False
    def __eq__(self, value, /):
        return bool(salah == value) or bool(False == value)
    def __ne__(self, value, /):
        return not self.__eq__(value)

class benar:
    def __init__(self):
        pass
    def __repr__(self):
        return 'benar'
    def __str__(self):
        return 'benar'
    def __int__(self):
        return 1
    def __float__(self):
        return 1.0
    def __bool__(self):
        return True
    def __eq__(self, value, /):
        return bool(benar == value) or bool(True == value)
    def __ne__(self, value, /):
        return not self.__eq__(value)

