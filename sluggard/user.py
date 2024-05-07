from .group import Group
from .dashboard import Dashboard
from .portfolio import Portfolio
from .exceptions import sluggardException

class User:
    def __init__(
        self, 
        user_id: str = None,
        username: str = None,
        primary_role: str = None,
        name: str = None,
        email: str = None,
        firstname: str = None,
        lastname: str = None,
        avatar: str = None,
        about: str = None,
        label: str = None,
        permalink: str = None,
        render_label: str = None,
        canBeImposter: str = None,
        groups: list[Group] = None,
        dashboards: list[Dashboard] = None,
        portfolios: list[Portfolio] = None,
        **kwargs
    ) -> None:
        self.user_id = user_id
        self.username = username
        self.primary_role = primary_role
        self.groups = groups
        self.dashboards = dashboards
        self.portfolios = portfolios
        self.avatar = avatar
        self.name = name
        self.about = about
        self.render_label = render_label
        self.canBeImposter = canBeImposter
        self.__dict__.update(kwargs)

    def __str__(self):
        return f"User({self.user_id}, {self.username}, {self.primary_role}, {self.avatar}))"

    @classmethod
    def discover_from_dict(cls, raw: dict):
        user_info = raw["data"]["user"]

        groups = [
            Group(
                group_id=group.get("id"),
                name=group.get("name"),
                typename=group.get("__typename"),
                icon=group.get("icon"),
                path=group.get("path"),
                link=group.get("permalink")
            )
            for group in user_info.get("groupsActive", [])
        ]

        dashboards = [
            Dashboard(
                dashboard_id=dashboard["id"],
                key=dashboard["key"],
                title=dashboard["title"],
                isHidden=dashboard["isHidden"],
                canBeHidden=dashboard["canBeHidden"]
            )
            for dashboard in user_info.get("dashboardTiles", [])
        ]

        return cls(
            user_id=user_info.get("id"),
            username=user_info.get("username"),
            avatar=user_info.get("avatar"),
            primary_role=user_info.get("primaryRole"),
            groups=groups,
            dashboards=dashboards
        )

    @classmethod
    def info_from_dict(cls, raw: dict):
        return cls(
            user_id=raw.get('id', ''),
            avatar=raw.get('avatar', ''),
            name=raw.get('name', ''),
            about=raw.get('about', ''),
            username=raw.get('username', ''),
            primary_role=raw.get('primary_role', ''),
            render_label=raw.get('render_label', ''),
            canBeImposter=raw.get('canBeImposter', '')
        )

    @classmethod
    def portfolio_from_dict(cls, raw: dict):
        portfolio_info = raw['data']['dashboard']['portfolioItems']['data']

        portfolios = [
            Portfolio(
                portfolio_id=portfolio['id'],
                icon=portfolio['icon'],
                title=portfolio['title'],
                link=portfolio['permalink'],
                creation_date=portfolio['createdAt'],
                author_id= portfolio['author']['id'],
                author_name= portfolio['author']['name']
            )
            for portfolio in portfolio_info
        ]

        return cls(portfolios=portfolios)
