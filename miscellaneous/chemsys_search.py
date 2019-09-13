
def search(input_chemsys, input_element):
    """

    :param input_chemsys: list of chemsys represented in string format
    :param input_element: testing element
    :return: list of chemsys that matches / contains input element
    """
    result = []
    for chemsys in input_chemsys:
        if input_element in chemsys:
            result.append(chemsys)
    return result


def test_search():
    assert search(["Li-Fe-O", "Fe-Li-O", "O-Fe-Li"], "Li") == ['Li-Fe-O', 'Fe-Li-O', 'O-Fe-Li']
    assert search(["Li-Fe-O", "Fe-Li-O", "O-Fe-Li"], "Li") != ['Li-Fe-O', 'Fe-Li-O']
    assert search(["Li-Fe-O", "Fe-Li-O", "O-Fe-Li", "Lol"], "Li") == ['Li-Fe-O', 'Fe-Li-O','O-Fe-Li']

