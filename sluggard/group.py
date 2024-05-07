class Group:
    def __init__(
        self,
        group_id: str = None,
        name: str = None,
        typename: str = None,
        icon: str = None,
        path: str = None,
        link: str = None
        ) -> None:
        
        self.group_id = group_id
        self.name = name
        self.typename = typename
        self.icon = icon
        self.path = path
        self.link = link