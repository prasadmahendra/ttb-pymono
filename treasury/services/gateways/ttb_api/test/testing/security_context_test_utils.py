class SecurityContextTestUtils:

    @staticmethod
    def mocked_role_decorator():
        # Mock the role_permissions_required decorator
        def role_decorator(*args, **kwargs):
            def wrapper(func):
                return func

            return wrapper

        return role_decorator
