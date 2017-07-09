"""py2rb-verbatim:
function foo(x) {
    print(x);
}
"""

"""py2rb-skip-begin"""
def foo(x):
    print(x)
"""py2rb-skip-end"""

foo('bar')
