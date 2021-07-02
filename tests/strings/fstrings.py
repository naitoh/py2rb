a = "dog\ndog\tdog"
b = 'cat'
c = '🐱'

print(f"001 {a}{b}{c}")
print(f'002 {a}{b}{c}')
print(f"""003 {a}{b}{c}""")

print(f"004 repr   {a!r} {b!r} {c!r}")
print(f"005 string {a!s} {b!s} {c!s}")
#broken print(f"006 ascii  {a!a} {b!a} {c!a}")

c = 1.234E-6
d = -177

print(f"float: {c} int: {d}")

e = (1, 3, 5)
f = ["b", 'c', 'd', 7]

print(f'tuple: {e} list: {f}')

print(f'tuple: {e!s} list: {f!s}')
print(f'tuple: {e!r} list: {f!r}')
#broken print(f'tuple: {e!a} list: {f!a}')

