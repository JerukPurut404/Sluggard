class Portfolio:
    def __init__(
        self, 
        static_banners,
        portfolio_id: str = None,
        icon: str = None,
        title: str = None,
        link: str = None,
        creation_date: int = None,
        author_id: str = None,
        author_name: str = None,
        banner_url: str = None,
        
    ) -> None:
        self.portfolio_id = portfolio_id
        self.icon = icon
        self.title = title 
        self.link = link
        self.creation_date = creation_date
        self.author_id = author_id
        self.author_name = author_name
        self.banner_url = banner_url
        self.static_banners = [Banner(banner['banner_filename'], banner['banner_url'], banner['banner_name'], banner['banner_group']) for banner in static_banners]

class Banner:
    def __init__(self, 
    filename: str = None,
    fileid: str = None,
    filesize: str = None,
    filetitle: str = None, 
    url: str = None, 
    name: str = None, 
    group: str = None
    ) -> None:
        self.filename = filename
        self.fileid = fileid
        self.filesize = filesize
        self.filetitle = filetitle
        self.url = url
        self.name = name
        self.group = group

    @classmethod
    def add_from_dict(cls, raw: dict):
        return cls(
            fileid=raw['file_id'],
            filesize=raw['file_size'],
            filetitle=raw['file_title']
            )

class Unsplash:
    def __init__(self,
    unsplash_id: str = None,
    unsplash_userid: str = None,
    unsplash_name: str = None,
    unsplash_permalink: str = None,
    unsplash_link: str = None,
    title: str = None,
    preview: str = None,
    perma_link: str = None,
    date: int = None,
    aspect_ratio: str = None,
    description: str = None,
    download_link: str = None,
    name: str = None,
    ) -> None:
        self.unsplash_id = unsplash_id
        self.title = title
        self.preview = preview
        self.perma_link = perma_link
        self.date = date
        self.aspect_ratio = aspect_ratio
        self.description = description
        self.download_link = download_link
        self.name = name
        self.unsplash_link = unsplash_link
        self.unsplash_name = unsplash_name
        self.unsplash_permalink = unsplash_permalink
    

