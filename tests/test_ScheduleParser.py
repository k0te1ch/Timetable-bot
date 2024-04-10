import pytest
from unittest.mock import patch
from utils.ScheduleParser import ScheduleParser
from pathlib import Path

@pytest.fixture
def sp():
    return ScheduleParser()

@patch('utils.ScheduleParser.requests.get')
@patch('utils.ScheduleParser.openpyxl.load_workbook')
def test_download_table(mock_load_workbook, mock_requests_get, sp):
    mock_requests_get.return_value.content = b'<html><a href="/d/123/"></a></html>'
    mock_load_workbook.return_value.active.max_row = 2
    mock_load_workbook.return_value.active.max_column = 2
    filename = sp._downloadTable()
    assert str(filename) == 'c:\\Users\\den03\\Timetable_bot\\files\\TimeTable.xlsx'  


def test_parse_not_empty():
    sp = ScheduleParser()

    parsed_table = sp._parse(Path('files/TimeTable.xlsx'))

    assert parsed_table is not None
    assert len(parsed_table) > 0  
    assert len(parsed_table[0]) > 0  

"""

def test_to_object(sp):
    table_data = [
        ['Course', 'Direction', 'Profile', 'Group', 'Num', 'Понедельник'],
        ['2 курс', 'Прикладная Информатика', 'Прикладная Информатика в Экономике', '13.1', 'Числитель', 'Методы вычислений в бизнес-приложениях доц. Копытин А.В. 295'],
    ]
    parsed_data = sp._toObject(table_data)
    
    assert parsed_data['2 курс']['Прикладная Информатика']['Прикладная Информатика в Экономике']['13.1']['Числитель']['Понедельник'] == 'Методы вычислений в бизнес-приложениях доц. Копытин А.В. 295'


def test_to_text(sp):
    input_data = {'1 курс': {'Direction A': {'Profile A': {'Group A': {'Числитель': {'Monday': 'Subject A'}}}}}}
    expected_output = '1 курс\n- Direction A\n-- Profile A\n--- Group A\n---- Числитель\n----- Monday: Subject A\n'
    
    result = sp._toText(input_data)
    
    assert result.strip() == expected_output.strip()

def test_get_schedule_for_day(sp):
    fake_data = {
        '1 курс': {
            'Direction A': {
                'Profile A': {
                    'Group A': {
                        'Числитель': {
                            'Monday': 'Subject A',
                            'Tuesday': 'Subject B'
                        },
                        'Знаменатель': {
                            'Monday': '',
                            'Tuesday': ''
                        }
                    }
                }
            }
        }
    }
    sp._tableObj = fake_data

    result = sp.getScheduleForDay('1 курс', 'Direction A', 'Profile A', 'Group A', 'Числитель', 'Monday')

    assert result == 'Monday (Числитель)\n- Subject A'

"""

def test_get_table_obj(sp):
    fake_data = {'fake': 'data'}
    sp._tableObj = fake_data
    
    assert sp.getTableObj() == fake_data

def test_get_free_audiences(sp):
    fake_data = {'Monday': {'8:00 - 9:35': {'Числитель': ['101', '102'], 'Знаменатель': ['103']}}}
    sp._freeAudiences = fake_data
    
    result = sp.getFreeAudiences('Monday', '8:00 - 9:35', 'Числитель')
    
    assert result == 'Вот список свободных аудиторий: 101, 102'