from dimod import BinaryQuadraticModel, DiscreteQuadraticModel
from dwave.system import DWaveSampler, EmbeddingComposite
import dimod
from dwave.system import LeapHybridCQMSampler
from .formulas import create_formula_tree
import operator


def solve_linear_program(variableCells, constraints, objectiveTarget, objectiveFormula):
    # print(variableCells)
    # print(constraints)
    # print(objectiveTarget)
    # print(objectiveFormula)
    qunatities = [dimod.Integer(f"{variable}") for variable in variableCells]
    print(qunatities)
    cqm = dimod.ConstrainedQuadraticModel()

    objectiveTree = create_formula_tree(variableCells, objectiveFormula)
    print(objectiveTree)

    def eval_tree_formula(qunatity, tree):
        eval_dict = {}
        for v, q in zip(variableCells, qunatity):
            eval_dict[v] = q
        return tree.eval(eval_dict)

    if objectiveTarget == "max":
        cqm.set_objective(-eval_tree_formula(qunatities, objectiveTree))
    elif objectiveTarget == "min":
        cqm.set_objective(eval_tree_formula(qunatities, objectiveTree))

    for constraint in constraints:
        (operator, l_tree, r_tree) = create_formula_tree(variableCells, constraint)
        print(operator, l_tree, r_tree)
        if operator == ">=":
            cqm.add_constraint(
                eval_tree_formula(qunatities, l_tree) >= r_tree.eval({}),
                label=f"f{l_tree}",
            )
        elif operator == "<=":
            cqm.add_constraint(
                eval_tree_formula(qunatities, l_tree) <= r_tree.eval({}),
                label=f"f{l_tree}",
            )
        elif operator == "==":
            cqm.add_constraint(
                eval_tree_formula(qunatities, l_tree) == r_tree.eval({}),
                label=f"f{l_tree}",
            )
    sampler = LeapHybridCQMSampler()
    sampleset = sampler.sample_cqm(cqm)
    feasible_sampleset = sampleset.filter(lambda row: row.is_feasible)
    print(
        "{} feasible solutions of {}.".format(len(feasible_sampleset), len(sampleset))
    )
    production = {
        drum: round(quantity, 1)
        for drum, quantity in feasible_sampleset.first.sample.items()
    }
    # print(production)
    return production
