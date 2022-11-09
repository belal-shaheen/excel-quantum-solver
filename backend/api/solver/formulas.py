import operator, random, math, copy

MAX_FLOAT = 1e12


def safe_division(numerator, denominator):
    """Divides numerator by denominator. If denominator is close to 0, returns
    MAX_FLOAT as an approximate of infinity."""
    if abs(denominator) <= 1 / MAX_FLOAT:
        return MAX_FLOAT
    return numerator / denominator


def safe_exp(power):
    """Takes e^power. If this results in a math overflow, or is greater
    than MAX_FLOAT, instead returns MAX_FLOAT"""
    try:
        result = math.exp(power)
        if result > MAX_FLOAT:
            return MAX_FLOAT
        return result
    except OverflowError:
        return MAX_FLOAT


FUNCTION_DICT = {
    "+": operator.add,
    "-": operator.sub,
    "*": operator.mul,
    "/": safe_division,
    "exp": safe_exp,
    "sin": math.sin,
    "cos": math.cos,
}

FUNCTION_KEYS = FUNCTION_DICT.keys()

FUNCTION_ARITIES = {"+": 2, "-": 2, "*": 2, "/": 2, "exp": 1, "sin": 1, "cos": 1}


class TerminalNode:
    """Leaf nodes that contain terminals."""

    def __init__(self, value, variables):
        """value might be a literal (i.e. 5.32), or a variable as a string."""
        self.value = value
        self.variables = variables

    def __str__(self):
        return str(self.value)

    def eval(self, variable_assignments):
        """Evaluates node given a dictionary of variable assignments."""

        if self.value in self.variables:
            return variable_assignments[self.value]

        return self.value

    def tree_depth(self):
        """Returns the total depth of tree rooted at this node.
        Since this is a terminal node, this is just 0."""

        return 0

    def size_of_subtree(self):
        """Gives the size of the subtree of this node, in number of nodes.
        Since this is a terminal node, this is just 1."""

        return 1


class FunctionNode:
    """Internal nodes that contain functions."""

    def __init__(self, function_symbol, children):
        self.function_symbol = function_symbol
        self.function = FUNCTION_DICT[self.function_symbol]
        self.children = children

        assert len(self.children) == FUNCTION_ARITIES[self.function_symbol]

    def __str__(self):
        """This should make printed programs look like Lisp."""

        result = f"({self.function_symbol}"
        for child in self.children:
            result += " " + str(child)
        result += ")"
        return result

    def eval(self, variable_assignments):
        """Evaluates node given a dictionary of variable assignments."""

        # Calculate the values of children nodes
        children_results = [child.eval(variable_assignments) for child in self.children]

        # Apply function to children_results.
        return self.function(*children_results)

    def tree_depth(self):
        """Returns the total depth of tree rooted at this node."""

        return 1 + max(child.tree_depth() for child in self.children)

    def size_of_subtree(self):
        """Gives the size of the subtree of this node, in number of nodes."""

        return 1 + sum(child.size_of_subtree() for child in self.children)


def create_formula_tree(variables, root):
    if root["type"] == "binary-expression" and root["operator"] in FUNCTION_KEYS:
        return FunctionNode(
            root["operator"],
            [
                create_formula_tree(variables, root["left"]),
                create_formula_tree(variables, root["right"]),
            ],
        )
    elif root["type"] == "binary-expression":
        return (
            root["operator"],
            create_formula_tree(variables, root["left"]),
            create_formula_tree(variables, root["right"]),
        )
    elif root["type"] == "cell":
        return TerminalNode(root["key"], variables)
    elif root["type"] == "number":
        return TerminalNode(int(root["value"]), variables)
    else:
        raise Exception("Unknown type")
