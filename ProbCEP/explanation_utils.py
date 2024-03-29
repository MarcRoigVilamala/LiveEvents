from sympy import Not, And, Or, Symbol
from sympy.logic.boolalg import to_dnf
from sympy.parsing.sympy_parser import parse_expr


def parse_explanation_list(explanations):
    res = {}

    for l in explanations:
        if l:  # Ignore empty lines
            query, body = l.split(" :- ")

            complex_event = query.split("=")[0].split("(")[1]
            timestamp = int(query.split(",")[-1][:-1])

            res.setdefault(complex_event, {})
            res[complex_event].setdefault(timestamp, [])

            if body != 'fail.':
                causes, probability = body.split(".  % P=")
                probability = float(probability)

                res[complex_event][timestamp].append(
                    (probability, causes)
                )

    return res


def extract_clauses_from(explanation_text):
    res = []

    for clause in explanation_text.split(', '):
        is_negated = False
        if clause.startswith('\\+'):
            is_negated = True
            clause = clause[2:]

        res.append(
            (is_negated, clause)
        )

    return res


def simplify_explanations(explanations, probabilities_by_clause, max_clauses=None):
    clause_to_id = {}
    id_to_clause = {}

    def get_clause_identifier(c):
        if c not in clause_to_id:
            identifier = "_{}".format(len(clause_to_id))
            clause_to_id[c] = identifier
            id_to_clause[identifier] = c

        return clause_to_id[c]

    def get_identifier_clause(identifier):
        return id_to_clause[identifier]

    def retranslate_explanation(expl):
        # Translates the explanation back from the sympy syntax into the ProbLog syntax.
        # Returns total probability and clauses, joined by a ","

        probability = 1.0

        retranslated_expl = []
        if isinstance(expl, (Symbol, Not)):
            to_iterate = [expl]  # If there is only one clause (instead of an And)
        elif isinstance(expl, And):
            to_iterate = expl.args
        else:
            raise ValueError("Unexpected type for explanation: {}".format(expl))

        for identifier in to_iterate:
            is_negated = False
            if isinstance(identifier, Not):
                identifier = identifier.args[0]
                is_negated = True

            clause = get_identifier_clause(str(identifier))

            if is_negated:
                retranslated_expl.append(
                    "\\+{}".format(
                        clause
                    )
                )
                probability *= 1 - probabilities_by_clause[clause]
            else:
                retranslated_expl.append(clause)
                probability *= probabilities_by_clause[clause]

        return probability, ", ".join(retranslated_expl)

    translated_expressions = []

    for current_expl in explanations:
        trans_exp = " & ".join(
            [
                "~{}".format(get_clause_identifier(clause)) if is_negated
                else get_clause_identifier(clause)
                for is_negated, clause in extract_clauses_from(current_expl[1])
            ]
        )

        if max_clauses and len(clause_to_id) > max_clauses:
            break

        translated_expressions.append(trans_exp)

    simplified_expression = to_dnf(
        parse_expr(
            " | ".join(translated_expressions)
        ),
        simplify=True,
        force=True
    )

    new_explanations = []
    if isinstance(simplified_expression, (And, Symbol, Not)):
        new_explanations = [retranslate_explanation(simplified_expression)]
    elif isinstance(simplified_expression, Or):
        for curr_expl in simplified_expression.args:
            new_explanations.append(retranslate_explanation(curr_expl))
    else:
        raise Exception(
            "Unexpected type for simplified expression {} of type {}".format(
                simplified_expression, type(simplified_expression)
            )
        )

    return new_explanations
