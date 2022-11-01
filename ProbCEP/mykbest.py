from problog import _evaluatables
from problog.cnf_formula import clarks_completion
from problog.core import transform
from problog.formula import LogicDAG
from problog.kbest import KBestFormula, KBestEvaluator, Border
from problog.logic import Term


class MyKBestFormula(KBestFormula):
    transform_preference = 40

    def _create_evaluator(self, semiring, weights, **kwargs):
        return MyKBestEvaluator(self, semiring=semiring, weights=weights, **kwargs)

    @classmethod
    def is_available(cls):
        """Checks whether the SDD library is available."""
        return True


transform(LogicDAG, MyKBestFormula, clarks_completion)
_evaluatables['mykbest'] = MyKBestFormula


class MyKBestEvaluator(KBestEvaluator):
    def __init__(self, formula, semiring, improvement_threshold=1e-6, **kwargs):
        super().__init__(formula=formula, semiring=semiring, **kwargs)

        self.improvement_threshold = improvement_threshold

    def evaluate(self, index):
        """Compute the value of the given node."""

        name = [n for n, i, l in self.formula.labeled() if i == index]
        if name:
            name = name[0]
        else:
            name = index

        if index is None:
            if self._explain is not None:
                self._explain.append("%s :- fail." % name)
            return 0.0
        elif index == 0:
            if self._explain is not None:
                self._explain.append("%s :- true." % name)
            return 1.0
        else:
            lb = Border(self.formula, self.sdd_manager, self.semiring, index, "lower")
            ub = Border(self.formula, self.sdd_manager, self.semiring, -index, "upper")

            k = 0
            # Select the border with most improvement
            if self._lower_only:
                nborder = lb
            else:
                nborder = max(lb, ub)

            while not nborder.is_complete():
                solution = nborder.update()
                if self._explain is not None and solution is not None:
                    solution_names = []

                    probability = nborder.improvement
                    for s in solution:
                        n = self._reverse_names.get(
                            abs(s), Term("choice_%s" % (abs(s)))
                        )
                        if s < 0:
                            solution_names.append(-n)
                        else:
                            solution_names.append(n)
                    proof = ", ".join(map(str, solution_names))
                    self._explain.append(
                        "%s :- %s.  %% P=%.8g" % (name, proof, probability)
                    )

                if solution is not None:
                    k += 1

                if nborder.is_complete() or nborder.improvement < self.improvement_threshold or k > 30:
                    if nborder == lb:
                        if self._explain is not None:
                            if k == 0:
                                self._explain.append("%s :- fail." % name)
                            self._explain.append("")
                        return lb.value
                    else:
                        return 1.0 - ub.value

                if ub.value + lb.value > 1.0 - self._convergence:
                    return lb.value, 1.0 - ub.value
                if self._lower_only:
                    nborder = lb
                else:
                    nborder = max(lb, ub)

            return lb.value, 1.0 - ub.value
