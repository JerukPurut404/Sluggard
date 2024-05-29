class Post:
    def __init__(self, post_data):
        self.post_id = post_data["post_id"]
        self.icon = post_data["icon"]
        self.title = post_data["title"]

class Author:
    def __init__(self, author_data):
        self.author_id = author_data["author_id"]
        self.name = author_data["name"]
        self.avatar = author_data["avatar"]
        self.username = author_data["username"]
        self.portfolioPermalink = author_data["portfolioPermalink"]

class Community:
    def __init__(
        self,
        community_id: str = None,
        posts: list[Post] = None,  
        authors: list[Author] = None  
    ) -> None:
        self.community_id = community_id
        self.posts = posts  
        self.authors = authors 

    def __str__(self):
        return f"Community({self.community_id})"

    @classmethod
    def from_dict(cls, raw: dict):
        post_info = raw['data']['activity']
        posts = [Post({
            "post_id": post.get("id"),
            "icon": post.get("icon"),
            "title": post.get("title")
        }) for post in post_info.get('portfolioRecentCommunityItems', [])]
        authors = [Author({
            "author_id": author.get("id"),
            "name": author.get("name"),
            "avatar": author.get("avatar"),
            "username": author.get("username"),
            "portfolioPermalink": author.get("portfolioPermalink")
        }) for author in post_info.get('author', [])]
        return cls(community_id=post_info["id"], posts=posts, authors=authors)
