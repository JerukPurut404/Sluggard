class School:
    def __init__(self, 
    school_id: str = None, 
    key: str = None, 
    logo: str = None, 
    name: str = None,
    sso: str = None, 
    link: str = None,
    idp_name: str = None,
    idp_logo: str = None,
    permalink: str = None
    ) -> None:
        self.school_id = school_id
        self.key = key
        self.logo = logo
        self.name = name
        self.sso = sso
        self.idp_name = idp_name
        self.idp_logo = idp_logo
        self.permalink = permalink

    @classmethod 
    def search__from__dict(cls, raw: dict):
        return cls(
            school_id=raw['id'],
            key=raw['key'],
            sso=raw['sso'],
            idp_name=raw['idp_name'],
            idp_logo=raw['idp_logo'],
            logo=raw['school_logo'],
            name=raw['school_name'],
            permalink=raw['school_permalink']
        )
