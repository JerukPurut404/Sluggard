class Portfolio:
    def __init__(
        self, 
        portfolio_id: str = None,
        icon: str = None,
        title: str = None,
        link: str = None,
        creation_date: int = None,
        author_id: str = None,
        author_name: str = None,

    ) -> None:
        self.portfolio_id = portfolio_id
        self.icon = icon
        self.title = title 
        self.link = link
        self.creation_date = creation_date
        self.author_id = author_id
        self.author_name = author_name

