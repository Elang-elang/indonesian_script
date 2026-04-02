from lark import Lark
from lark_rust import plugins

parser = Lark(
    open('./gramm.lark', 'r').read(),
    parser='lalr', # 'earley',
    cache=True,
    regex=True,
    debug=True,
    keep_all_tokens=True,
    maybe_placeholders=True,
)


print(dir(parser))
tree = parser.parse("""var[angka] angkA = 1;""")

print(tree)
print(dir(tree))