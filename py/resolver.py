from .service import Service


class Resolver:
    service_a: Service
    service_b: Service

    def __init__(self, types: tuple[type, type], config: dict = {}) -> None:
        assert issubclass(types[0], Service)
        assert issubclass(types[1], Service)
        print(
            f"Converting content from service {types[0].__name__} to service {types[1].__name__}"
        )

        service_a = types[0]()
        service_b = types[1]()

        service_a.get_user_content()
        service_b.get_user_content()
