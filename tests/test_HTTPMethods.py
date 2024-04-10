'''
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from utils.HTTPMethods import getMyIp, downloadFileBot, downloadFile

@pytest.mark.asyncio
async def test_getMyIp():
    mock_session = AsyncMock()
    mock_response = AsyncMock()
    mock_response.json.return_value = {"ip": "127.0.0.1"}
    mock_session.get.return_value.__aenter__.return_value = mock_response

    with patch('utils.HTTPMethods.getMyIp') as mock_get_my_ip:
        mock_get_my_ip.return_value = mock_session


        print(getMyIp)
        result = await getMyIp()
        print("result=", result)

        assert result == "127.0.0.1"


@pytest.mark.asyncio
async def test_downloadFileBot():
    with patch('utils.HTTPMethods.getMyIp') as mock_get_session:
        mock_session = MagicMock()
        mock_get_session.return_value = mock_session

        mock_response = AsyncMock()
        mock_response.content.read = AsyncMock(side_effect=[b'data_chunk1', b'data_chunk2', b''])
        mock_session.get.return_value.__aenter__.return_value = mock_response

        await downloadFileBot("https://example.com/file", "test_file.txt")
        
        with open("test_file.txt", "rb") as file:
            assert file.read() == b'data_chunk1data_chunk2'

def test_downloadFile(tmp_path):
    test_file = tmp_path / "test_file.txt"

    with patch('utils.HTTPMethods.requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b'data_chunk1', b'data_chunk2']
        mock_get.return_value.__enter__.return_value = mock_response

        downloadFile("https://example.com/file", str(test_file))
        
        assert test_file.read_text() == 'data_chunk1data_chunk2'
        '''
