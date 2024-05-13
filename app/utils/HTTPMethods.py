from loguru import logger

# FIXME: this module


@logger.catch
async def getMyIp() -> str:
    """
    Getting the bot's IP address
    :return: str
    """
    from bot import bot

    session = await bot.get_session()
    async with session.get("https://ipinfo.io/json") as r:
        jdata = await r.json()
        logger.opt(colors=True).debug("Get IP")
        return jdata.get("ip")


@logger.catch
async def downloadFileBot(url: str, filename: str, chunkSize: int = 65536) -> None:
    """
    Download file async and by bot session
    :param: url
    :param: filename
    :param: chunkSize = 65536
    :return: None
    """
    logger.opt(colors=True).debug(f"The file started downloading <y>({filename})</y>")
    from bot import bot

    session = await bot.get_session()
    async with session.get(
        url,
        raise_for_status=True,
    ) as response:
        file = open(filename, "wb")
        while True:
            chunk = await response.content.read(chunkSize)
            if not chunk:
                break
            file.write(chunk)
            file.flush()
        file.close()
    logger.opt(colors=True).debug(f"<g>File downloaded <y>({filename})</y></g>")


@logger.catch
def downloadFile(url: str, filename: str, chunkSize: int = 65536) -> None:
    """
    Download file sync
    :param: url
    :param: filename
    :param: chunkSize = 65536
    :return: None
    """
    import requests

    logger.opt(colors=True).debug(f"The file started downloading <y>({filename})</y>")
    with requests.get(url, stream=True) as response:
        response.raise_for_status()
        with open(filename, "wb") as file:
            for chunk in response.iter_content(chunk_size=chunkSize):
                if chunk:
                    file.write(chunk)
    logger.opt(colors=True).debug(f"<g>File downloaded <y>({filename})</y></g>")
