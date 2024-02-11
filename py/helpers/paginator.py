from ..service import LocalLibraryContentError


class Paginator:

    def __init__(self, get_records_list, parse_record, limit, total) -> list:
        """
        Parameters
        ------------
            get_records_list: callable
                Returns a tuple containing the JSON record list, as well
                as the next offset to call. Return -1 if the pages are exhausted.

            parse_record: callable
                Returns a single record of any type (i.e. dataclass type) to be added to the full collection
                contained in this class.

        Returns
        ------------
            list:
                Returns the parsed records

        """

        self.get_records_list = get_records_list
        self.parse_record = parse_record

        self.records = []

        NUM_THREADS = 10

        chunks = total // limit + 1
        chunks_per_thread = chunks // NUM_THREADS
        chunks_remainder = chunks % NUM_THREADS

        threadcounts = [
            (chunks_per_thread + 1 if i < chunks_remainder else chunks_per_thread)
            * limit
            for i in range(NUM_THREADS)
        ]
        print(threadcounts)

        offsets = []
        offsets.append(0)

        for i in range(1, len(threadcounts)):
            offsets.append(threadcounts[i] + offsets[i - 1])

        print(offsets)

        offset: int = 0

        while True:

            (records, offset) = get_records_list(offset)
            print(offset)
            for record in records:
                try:
                    self.records.append(self.parse_record(record))
                except LocalLibraryContentError:
                    pass

            if offset < 0:
                break

    def __iter__(self):
        yield from self.records
