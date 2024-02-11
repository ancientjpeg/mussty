from ..service import LocalLibraryContentError
import asyncio
import aiohttp


class Paginator:
    lock: asyncio.Lock
    session: aiohttp.ClientSession

    def __init__(self, get_records_list, limit, total) -> None:

        async def get_records(self, get_records_list, limit, total) -> list:
            """
            Parameters
            ------------
                get_records_list: callable
                    Returns a tuple containing the JSON record list, as well
                    as the next offset to call. Return -1 if the pages are exhausted.

            Returns
            ------------
                list:
                    Returns the parsed records

            """

            num_tasks = total // limit + 1
            task_results = [[]] * num_tasks

            offsets = [i * limit for i in range(num_tasks)]

            tg: asyncio.TaskGroup
            self.lock = asyncio.Lock()
            task_results = []
            async with aiohttp.ClientSession() as self.session:
                async with asyncio.TaskGroup() as tg:
                    for i in range(len(offsets)):
                        task_result = tg.create_task(
                            get_records_list(i, offsets[i], self)
                        )
                        task_results.append(task_result)

            print(task_results[0].result())
            exit()

        asyncio.run(get_records(self, get_records_list, limit, total))

    def __iter__(self):
        yield from self.records
