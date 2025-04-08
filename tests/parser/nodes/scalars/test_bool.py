import pytest

from ftml import load, FTMLParseError


# Root-level bool values are no longer allowed

def test_true_should_fail():
    ftml_input = "true"
    with pytest.raises(FTMLParseError):
        data = load(ftml_input)


def test_true_with_key():
    ftml_input = "my_key = true"
    data = load(ftml_input)
    assert data["my_key"] is True


def test_false_should_fail():
    ftml_input = "false"
    with pytest.raises(FTMLParseError):
        data = load(ftml_input)


def test_false_with_key():
    ftml_input = "my_key = false"
    data = load(ftml_input)
    assert data["my_key"] is False


def test_true_uppercase_should_fail():
    ftml_input = "my_key = True"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_false_uppercase_should_fail():
    ftml_input = "my_key = False"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_true_in_double_quotes_should_fail():
    ftml_input = '"true"'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_true_in_double_quotes_with_key():
    ftml_input = "my_key = \"true\""
    data = load(ftml_input)
    assert data["my_key"] == "true"


def test_false_in_double_quotes_should_fail():
    ftml_input = '"false"'
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_false_in_double_quotes_with_key():
    ftml_input = "my_key = \"false\""
    data = load(ftml_input)
    assert data["my_key"] == "false"


def test_true_in_single_quotes_should_fail():
    ftml_input = "'true'"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_true_in_single_quotes_with_key():
    ftml_input = "my_key = 'true'"
    data = load(ftml_input)
    assert data["my_key"] == "true"


def test_false_in_single_quotes_should_fail():
    ftml_input = "'false'"
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_false_in_single_quotes_with_key():
    ftml_input = "my_key = 'false'"
    data = load(ftml_input)
    assert data["my_key"] == "false"


def test_true_with_extra_whitespace_should_fail():
    ftml_input = "  true  "
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_true_with_extra_whitespace_and_key():
    ftml_input = "my_key =   true"
    data = load(ftml_input)
    assert data["my_key"] is True


def test_false_with_extra_whitespace_should_fail():
    ftml_input = "  false  "
    with pytest.raises(FTMLParseError):
        load(ftml_input)


def test_false_with_extra_whitespace_and_key():
    ftml_input = "my_key =   false  "
    data = load(ftml_input)
    assert data["my_key"] is False
