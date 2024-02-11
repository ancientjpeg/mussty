from ..service import LocalLibraryContentError


class Paginator:

    def __init__(self, get_records_list, parse_record) -> list:
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

        offset: int = 0

        while True:

            (records, offset) = get_records_list(offset)
            for record in records:
                try:
                    self.records.append(self.parse_record(record))
                except LocalLibraryContentError:
                    pass

            if offset < 0:
                break

        return self.records
