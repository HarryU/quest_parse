import pytest
from bs4 import BeautifulSoup
import urllib.request


@pytest.fixture
def quest_table():
    return "<table class=\"questreq\"><tbody><li>content</li></tbody></table>"


@pytest.fixture
def input_html():
    return  "<html><table class=\"this\"><tbody></tbody></table><table class=\"questreq\"><tbody><li>content</li></tbody></table><\html>"


def test_gets_table_by_class(input_html, quest_table):
    assert get_table(input_html, 'questreq') == quest_table


def test_gets_differet_table_by_class(input_html):
    other_table =  "<table class=\"this\"><tbody></tbody></table>"
    assert get_table(input_html, 'this') == other_table

def test_only_gives_a_table(quest_table):
    input_html = "<html><table class=\"this\"><tbody></tbody></table><p class=\"questreq\"></p><table class=\"questreq\"><tbody><li>content</li></tbody></table><\html>"
    assert get_table(input_html, 'questreq') == quest_table


def test_gets_table_list_item_contents(quest_table):
    assert get_list_item_contents(quest_table) == ["content"]


def test_gets_different_list_item_contents():
    table = "<table class=\"questreq\"><tbody><li>other</li></tbody></table>"
    assert get_list_item_contents(table) == ["other"]


def test_gets_multiple_list_items():
    table = "<table class=\"questreq\"><tbody><li>content</li><li>other</li></tbody></table>"
    assert get_list_item_contents(table) == ["content", "other"]


def test_correctly_parses_nested_list():
    table = "<table class=\"questreq\"><tbody><li><li>content</li><li>other</li></li></tbody></table>"
    assert get_list_item_contents(table) == ["content", "other"]


def get_table(html, desired_class):
    soup = BeautifulSoup(html, 'html.parser')
    return str(soup.find('table', class_=desired_class))


def get_list_item_contents(table):
    soup = BeautifulSoup(table, 'html.parser')
    list_items = soup.find_all('li')
    return [''.join(result.find_all(text=True)) for result in list_items]


if __name__ == "__main__":
    url = "https://runescape.wiki/w/The_Temple_at_Senntisten"
    req = urllib.request.Request(url, headers={'User-Agent' : "Magic Browser"})
    html = urllib.request.urlopen(req).read()
    print(get_list_item_contents(get_table(html, 'questreq'))[0])

